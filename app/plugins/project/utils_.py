from collections import OrderedDict
from dataclasses import dataclass
from time import perf_counter
from types import SimpleNamespace

from PySide2.QtCore import Qt

from app import app_logger
from db import sp

logger = app_logger.get_logger(__name__)
_project_param_names_cache = {}
_project_params_cache = {}
_param_values_cache = {}


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


def collect_project_params(db_objects):
    params = {}
    for o in db_objects:
        if o.prop_name == 'name':
            params[o.excel_param_name] = o
    return params


def get_project_param_names(project_id, force_reload=False):
    """Return cached project parameter names for combo/search UI."""
    if not force_reload and project_id in _project_param_names_cache:
        result = _project_param_names_cache[project_id]
        logger.info("Project param names cache hit: project_id=%s, params=%s", project_id, len(result))
        return result

    started = perf_counter()
    result = [name for name in (sp.get_project_param_names(project_id) or []) if name]
    _project_param_names_cache[project_id] = result
    logger.info("Project param names loaded: project_id=%s, params=%s, elapsed_ms=%.1f",
                project_id, len(result), (perf_counter() - started) * 1000)
    return result


def get_project_params(project_id, force_reload=False):
    """Return a lightweight, cached parameter map compatible with old UI code."""
    if not force_reload and project_id in _project_params_cache:
        result = _project_params_cache[project_id]
        logger.info("Project param names cache hit: project_id=%s, params=%s", project_id, len(result))
        return result

    names = get_project_param_names(project_id, force_reload=force_reload)
    result = {name: SimpleNamespace(prop_name='name', excel_param_name=name) for name in names}
    _project_params_cache[project_id] = result
    return result


def get_param_values(project_id, param_name, force_reload=False):
    """Load values lazily for one parameter and cache them."""
    key = project_id, param_name
    if not force_reload and key in _param_values_cache:
        logger.debug("Param values cache hit: project_id=%s, param=%s", project_id, param_name)
        return _param_values_cache[key]
    logger.debug("Param values cache miss: project_id=%s, param=%s", project_id, param_name)
    started = perf_counter()
    result = sp.get_params_values([param_name], project_id) or []
    _param_values_cache[key] = result
    logger.info("Project param values loaded: project_id=%s, param=%s, values=%s, elapsed_ms=%.1f",
                project_id, param_name, len(result), (perf_counter() - started) * 1000)
    return result


def clear_project_params(project_id=None):
    """Invalidate parameter names and values for one project, or all projects."""
    if project_id is None:
        _project_param_names_cache.clear()
        _project_params_cache.clear()
        _param_values_cache.clear()
        logger.debug("Project param caches cleared: all projects")
        return
    _project_param_names_cache.pop(project_id, None)
    _project_params_cache.pop(project_id, None)
    for key in [key for key in _param_values_cache if key[0] == project_id]:
        _param_values_cache.pop(key, None)
    logger.debug("Project param caches cleared: project_id=%s", project_id)


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
