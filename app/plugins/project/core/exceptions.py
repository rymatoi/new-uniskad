# core/exceptions.py
class GraphException(Exception):
    """Базовое исключение для графических операций"""


class EpureException(Exception):
    """Базовое исключение для операций над эпюрами"""


class InvalidCurveDataError(GraphException):
    """Некорректные данные кривой"""


class InvalidInterpolationMethod:
    """Некорректный метод интерполяции"""


class InvalidPointValueError(GraphException):
    """Некорректное значение точки"""


class EpureAttributeError(GraphException):
    """Отсутствие нужного атрибута для построения эпюр"""
