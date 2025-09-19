from PySide2.QtCore import Qt
from PySide2.QtGui import QColor


class GraphConstants:
    LINE_STYLES = {
        0: Qt.NoPen,
        1: Qt.SolidLine,
        2: Qt.DashLine,
        3: Qt.DotLine
    }

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
        'symbol_size': 8
    }

    APPROXIMATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': None,
        'symbol_size': 2
    }

    INTERPOLATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': None,
        'symbol_size': 2
    }

    EXTRAPOLATION_STYLE = {
        'color': '#1f77b4',
        'width': 2,
        'line_style': 'solid',
        'symbol': None,
        'symbol_size': 2
    }
