from PySide2.QtCore import Qt
from PySide2.QtGui import QColor


class GraphConstants:
    LINE_STYLES = {
        0: Qt.NoPen,
        1: Qt.SolidLine,
        2: Qt.DashLine,
        3: Qt.DotLine,
        4: Qt.DashDotLine,
        5: Qt.DashDotDotLine,
    }

    STRING_LINE_STYLES = {
        'none': Qt.NoPen,
        'solid': Qt.SolidLine,
        'dash': Qt.DashLine,
        'dot': Qt.DotLine,
        'dashdot': Qt.DashDotLine,
        'dashdotdot': Qt.DashDotDotLine,
    }

    @classmethod
    def resolve_pen_style(cls, value):
        """Convert stored style value to a Qt pen style."""
        if value is None:
            return Qt.SolidLine

        # value can already be Qt.PenStyle or int compatible with mapping
        if isinstance(value, int):
            return cls.LINE_STYLES.get(value, Qt.SolidLine)

        # Strings are used in default styles
        if isinstance(value, str):
            return cls.STRING_LINE_STYLES.get(value.lower(), Qt.SolidLine)

        # Fallback for Qt.PenStyle or unexpected type
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            return Qt.SolidLine
        return cls.LINE_STYLES.get(int_value, Qt.SolidLine)

    DEFAULT_COLORS = [
        QColor('#1f77b4'),  # blue
        QColor('#ff7f0e'),  # orange
        QColor('#2ca02c')  # green
    ]

    DEFAULT_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': 'o',
        'symbol_size': 8,
        'symbol_color': '#1f77b4',
    }

    # Настройки построения эпюр
    EPURE_INTERPOLATION_MULTIPLIER = 25
    EPURE_INTERPOLATION_MIN_POINTS = 64
    EPURE_INTERPOLATION_MAX_POINTS = 512
    EPURE_DIRECT_DRAW_THRESHOLD = 3

    APPROXIMATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': DEFAULT_STYLE['symbol'],
        'symbol_size': DEFAULT_STYLE['symbol_size'],
        'symbol_color': DEFAULT_STYLE['symbol_color'],
    }

    INTERPOLATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': None,
        'symbol_size': 2,
        'symbol_color': '#1f77b4',
    }

    EXTRAPOLATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': None,
        'symbol_size': 2,
        'symbol_color': '#1f77b4',
    }
