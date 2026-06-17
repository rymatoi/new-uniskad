from collections import OrderedDict
from dataclasses import dataclass
import ast
import json
from time import perf_counter
from types import SimpleNamespace

from PySide2.QtCore import Qt

from app import app_logger
from db import sp

logger = app_logger.get_logger(__name__)
_project_param_names_cache = {}
_project_params_cache = {}
_param_values_cache = {}


def build_graph_name(x_param: str, y_param: str) -> str:
    """Build the default graph name from axis parameter names."""
    return f'{y_param or ""} от {x_param or ""}'


@dataclass
class Values:
    max_val: float
    min_val: float
LINE_STYLES = [
    (Qt.NoPen, 'Прозрачная'),
    (Qt.SolidLine, 'Линия'),
    (Qt.DashLine, 'Пунктирная линия'),
    (Qt.DotLine, 'Линия из точек'),
    (Qt.DashDotLine, 'Линия точка-тире'),
    (Qt.DashDotDotLine, 'Линия точка-точка-тире'),
]

COLORS = [
    'Red',  # ff0000
    'Green',  # 00ff00
    'Blue',  # 0000ff
    'Cyan',  # 00ffff
    'Magenta',  # ff00ff
    'Yellow',  # ffff00
    'DarkRed',  # 800000
    'DarkGreen',  # 008000
    'DarkBlue',  # 000080
    'DarkCyan',  # 008080
    'DarkMagenta',  # 800080
    'DarkYellow',  # 808000
    'DarkGray',  # 808080
    'Gray',  # a0a0a4
    'LightGray',  # c0c0c0

]

SYMBOLS = [
    ('o', 'Круг'),  # Default symbol, round circle symbol
    ('s', 'Квадрат'),  # Square symbol
    ('t1', 'Треугольник вверх'),  # Triangle pointing upwards symbol
    ('d', 'Ромб'),  # Prism symbol
    ('star', 'Звезда'),  # Star symbol
    ('p', 'Пятиугольник'),  # Pentagon symbol
    ('h', 'Восьмиугольник'),  # Hexagon symbol
    ('x', 'Крест'),  # Cross symbol
    ('+', 'Плюс'),  # Plus symbol
    ('t', 'Треугольник вниз'),  # Triangle pointing downwards symbol
    ('t2', 'Треугольник вправо'),  # Triangle pointing right side symbol
    ('t3', 'Треугольник влево'),  # Triangle pointing left side symbol
]

# *'arrow_up'
# *'arrow_right'
# *'arrow_down'
# *'arrow_left'
# *'crosshair'


def get_next_default_combination(num):
    return LINE_STYLES[num % len(LINE_STYLES)], COLORS[num % len(COLORS)], SYMBOLS[num % len(SYMBOLS)][0]



def parse_list_value(value):
    """Safely coerce stored list-like project fields to a Python list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            logger.debug("Could not parse list-like value", exc_info=True)
            return []
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, tuple):
            return list(parsed)
    return []


def parse_json_or_literal_value(value, default=None):
    """Safely parse JSON/Python-literal containers without reparsing ready objects."""
    if isinstance(value, (dict, list, tuple)):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        for parser in (json.loads, ast.literal_eval):
            try:
                return parser(text)
            except (ValueError, SyntaxError, TypeError):
                continue
        logger.debug("Could not parse JSON/literal project value: %r", value)
    return default

def collect_project_params(db_objects):
    params = {}
    for o in db_objects:
        if o.prop_name == 'name':
            params[o.excel_param_name] = o
    return params


def get_project_param_names(project_id, force_reload=False):
    """Return cached project parameter names for combo/search UI."""
    cache_key = int(project_id)
    if not force_reload and cache_key in _project_param_names_cache:
        result = _project_param_names_cache[cache_key]
        logger.info("Project param names cache hit: project_id=%s, params=%s", project_id, len(result))
        return result

    started = perf_counter()
    result = [name for name in (sp.get_project_param_names(project_id) or []) if name]
    _project_param_names_cache[cache_key] = result
    logger.info("Project param names loaded: project_id=%s, params=%s, elapsed_ms=%.1f",
                project_id, len(result), (perf_counter() - started) * 1000)
    return result


def get_project_params(project_id, force_reload=False):
    """Return a lightweight, cached parameter map compatible with old UI code."""
    cache_key = int(project_id)
    if not force_reload and cache_key in _project_params_cache:
        result = _project_params_cache[cache_key]
        logger.info("Project param names cache hit: project_id=%s, params=%s", project_id, len(result))
        return result

    names = get_project_param_names(project_id, force_reload=force_reload)
    result = {name: SimpleNamespace(prop_name='name', excel_param_name=name) for name in names}
    _project_params_cache[cache_key] = result
    return result


def get_param_values(project_id, param_name, force_reload=False):
    """Load values lazily for one parameter and cache them."""
    if param_name is None or str(param_name) == '':
        logger.info("Project param values skipped: project_id=%s, param=%r", project_id, param_name)
        return []

    key = int(project_id), str(param_name)
    if not force_reload and key in _param_values_cache:
        values = _param_values_cache[key]
        logger.info(
            "Project param values cache hit: project_id=%s, param=%r, values=%s",
            project_id, param_name, len(values),
        )
        return values

    started = perf_counter()
    values = sp.get_params_values([str(param_name)], project_id) or []
    _param_values_cache[key] = values
    logger.info(
        "Project param values loaded: project_id=%s, param=%r, values=%s, elapsed_ms=%.1f",
        project_id, param_name, len(values), (perf_counter() - started) * 1000,
    )
    return values


def clear_project_param_cache(project_id=None):
    """Invalidate cached project parameter names and values for one project, or all projects."""
    if project_id is None:
        names_removed = len(_project_param_names_cache) + len(_project_params_cache)
        values_removed = len(_param_values_cache)
        _project_param_names_cache.clear()
        _project_params_cache.clear()
        _param_values_cache.clear()
        logger.info(
            "Project param cache cleared: all projects, names_removed=%s, values_removed=%s",
            names_removed, values_removed,
        )
        return

    cache_key = int(project_id)
    names_removed = int(_project_param_names_cache.pop(cache_key, None) is not None)
    names_removed += int(_project_params_cache.pop(cache_key, None) is not None)
    value_keys = [key for key in _param_values_cache if key[0] == cache_key]
    for key in value_keys:
        _param_values_cache.pop(key, None)
    logger.info(
        "Project param cache cleared: project_id=%s, names_removed=%s, values_removed=%s",
        project_id, names_removed, len(value_keys),
    )


def resolve_project_param_cache_project_id(item=None, data=None):
    """Return the root project id used by project parameter loaders.

    Parameter names and values are loaded with the root project node id, not
    necessarily the currently edited tree item id (for example graph/test ids).
    Prefer the nearest ancestor ProjectNode when a tree item is available.
    """
    current = item
    while current is not None:
        current_data = getattr(current, '_data', None)
        internal_type = getattr(current, 'internal_type', None)
        try:
            if callable(internal_type) and internal_type() == 'project':
                return getattr(current_data, 'id', None) or getattr(current_data, 'project_id', None)
        except Exception:
            logger.debug("Could not resolve project param cache id from item ancestor", exc_info=True)
            break
        parent = getattr(current, 'parent', None)
        current = parent() if callable(parent) else None

    data = data or getattr(item, '_data', None)
    if data is None:
        return None

    return (
        getattr(data, 'project_id_up', None)
        or getattr(data, 'id_up', None)
        or getattr(data, 'project_id', None)
        or getattr(data, 'id', None)
    )


def invalidate_project_param_cache_after_update(item_id=None, cache_project_id=None, item=None, data=None):
    """Invalidate parameter cache after a successful write using the loader project id."""
    actual_project_id = cache_project_id
    if actual_project_id is None:
        actual_project_id = resolve_project_param_cache_project_id(item=item, data=data)
    if item_id is None:
        source_data = data or getattr(item, '_data', None)
        item_id = getattr(source_data, 'id', None) or getattr(source_data, 'project_id', None)

    logger.info(
        "Invalidating project param cache after project data update: item_id=%s, cache_project_id=%s",
        item_id, actual_project_id,
    )
    if actual_project_id is None:
        clear_project_param_cache()
    else:
        clear_project_param_cache(actual_project_id)


def clear_project_params(project_id=None):
    """Backward-compatible alias for clear_project_param_cache."""
    clear_project_param_cache(project_id)


def collect_cell_values(db_objects):
    operated = OrderedDict()
    broken_keys = []
    for o in db_objects:
        key = o.excel_param_name, o.date_time_izm, o.project_id
        if o.prop_name == 'broken' and o.prop_value == 'True':
            if key not in broken_keys:
                broken_keys.append(key)
        elif o.prop_name == 'broken' and o.prop_value == 'False':
            if key in broken_keys:
                broken_keys.remove(key)
        if o.prop_name == 'cformula':
            operated[key] = o
        elif o.prop_name == 'value':
            if key not in operated:
                operated[key] = o

    result = {}
    for o in list(operated.values()):
        key = o.excel_param_name, o.project_id
        if key not in result:
            result[key] = []
        if (o.excel_param_name, o.date_time_izm, o.project_id) in broken_keys:
            o.prop_value = None
        result[key].append(o)

    return result


def compare_floats(num1, num2):
    # Преобразуем числа в строки для определения количества знаков после запятой
    str_num1 = f"{num1:.10f}".rstrip('0').rstrip('.')
    str_num2 = f"{num2:.10f}".rstrip('0').rstrip('.')

    # Определяем количество знаков после запятой у каждого числа
    decimal_places1 = len(str_num1.split('.')[1]) if '.' in str_num1 else 0
    decimal_places2 = len(str_num2.split('.')[1]) if '.' in str_num2 else 0

    # Определяем минимальное количество знаков после запятой
    decimal_places = min(decimal_places1, decimal_places2)

    # Округляем числа до минимального количества знаков после запятой
    rounded_num1 = round(num1, decimal_places)
    rounded_num2 = round(num2, decimal_places)

    # Сравниваем округленные числа
    return rounded_num1 == rounded_num2
