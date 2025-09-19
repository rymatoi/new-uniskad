from collections import OrderedDict

from PySide2.QtCore import Qt

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
