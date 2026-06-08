from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class GraphConstants:
    LINE_STYLES = {
        0: Qt.PenStyle.NoPen,
        1: Qt.PenStyle.SolidLine,
        2: Qt.PenStyle.DashLine,
        3: Qt.PenStyle.DotLine,
        4: Qt.PenStyle.DashDotLine,
        5: Qt.PenStyle.DashDotDotLine,
    }

    STRING_LINE_STYLES = {
        'none': Qt.PenStyle.NoPen,
        'solid': Qt.PenStyle.SolidLine,
        'dash': Qt.PenStyle.DashLine,
        'dot': Qt.PenStyle.DotLine,
        'dashdot': Qt.PenStyle.DashDotLine,
        'dashdotdot': Qt.PenStyle.DashDotDotLine,
    }

    @classmethod
    def resolve_pen_style(cls, value):
        """Convert stored style value to a Qt pen style."""
        if value is None:
            return Qt.PenStyle.SolidLine

        # value can already be Qt.PenStyle or int compatible with mapping
        if isinstance(value, int):
            return cls.LINE_STYLES.get(value, Qt.PenStyle.SolidLine)

        # Strings are used in default styles
        if isinstance(value, str):
            return cls.STRING_LINE_STYLES.get(value.lower(), Qt.PenStyle.SolidLine)

        # Fallback for Qt.PenStyle or unexpected type
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            return Qt.PenStyle.SolidLine
        return cls.LINE_STYLES.get(int_value, Qt.PenStyle.SolidLine)

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
        'symbol': None,
        'symbol_size': 2,
        'symbol_color': '#1f77b4',
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
