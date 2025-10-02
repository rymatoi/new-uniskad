from PySide2.QtCore import QPointF
from PySide2.QtGui import QPainter
import pyqtgraph as pg
from pyqtgraph.graphicsItems.LegendItem import ItemSample


class CurveWithPointsSample(ItemSample):
    """Отрисовка образца легенды для эпюр с линией и точкой."""

    def __init__(self, item):
        super().__init__(item)
        self.item = item

    def paint(self, painter: QPainter, *args):  # type: ignore[override]
        rect = self.boundingRect()
        center_y = rect.center().y()
        left = rect.left() + 2
        right = rect.right() - 2

        opts = getattr(self.item, 'opts', {})

        pen = opts.get('pen', None)
        if pen is not None:
            painter.setPen(pg.mkPen(pen))
            painter.drawLine(left, center_y, right, center_y)

        symbol = opts.get('symbol')
        if not symbol:
            return

        size = opts.get('symbolSize', 8)
        symbol_pen = pg.mkPen(opts.get('symbolPen', pen))
        symbol_brush = pg.mkBrush(opts.get('symbolBrush', None))

        painter.setPen(symbol_pen)
        painter.setBrush(symbol_brush)

        try:
            from pyqtgraph.graphicsItems.ScatterPlot import drawSymbol

            drawSymbol(
                painter,
                symbol,
                size,
                QPointF((left + right) / 2, center_y),
                symbol_brush,
                symbol_pen,
            )
        except Exception:
            radius = size / 2
            painter.drawEllipse(QPointF((left + right) / 2, center_y), radius, radius)
