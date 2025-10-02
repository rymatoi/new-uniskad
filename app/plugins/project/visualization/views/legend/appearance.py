from dataclasses import dataclass

from PySide2.QtGui import QColor
import pyqtgraph as pg


def _to_qcolor(value) -> QColor:
    if isinstance(value, QColor):
        return QColor(value)
    color = QColor()
    if isinstance(value, (tuple, list)) and len(value) >= 3:
        color.setRgb(*value[:3])
        if len(value) == 4:
            color.setAlpha(value[3])
        return color
    if isinstance(value, str):
        color.setNamedColor(value)
        if color.isValid():
            return color
    if hasattr(value, 'red') and hasattr(value, 'green') and hasattr(value, 'blue'):
        color = QColor(value.red(), value.green(), value.blue(), value.alpha())
        return color
    raise ValueError('Unsupported color value: %r' % (value,))


@dataclass
class LegendAppearance:
    background: QColor
    border: QColor
    opacity: int = 255
    border_width: int = 1

    @classmethod
    def default(cls) -> "LegendAppearance":
        return cls(QColor(255, 255, 255), QColor(100, 100, 100), 255, 1)

    def with_background(self, color) -> "LegendAppearance":
        return LegendAppearance(_to_qcolor(color), self.border, self.opacity, self.border_width)

    def with_border(self, color, width=None) -> "LegendAppearance":
        return LegendAppearance(self.background, _to_qcolor(color), self.opacity, self.border_width if width is None else width)

    def with_opacity(self, opacity: int) -> "LegendAppearance":
        return LegendAppearance(self.background, self.border, max(0, min(255, int(opacity))), self.border_width)

    def to_brush(self):
        color = QColor(self.background)
        color.setAlpha(max(0, min(255, int(self.opacity))))
        return pg.mkBrush(color)

    def to_pen(self):
        color = QColor(self.border)
        return pg.mkPen(color=color, width=max(1, int(self.border_width)))
