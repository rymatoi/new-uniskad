from typing import Optional

import pyqtgraph as pg
from pyqtgraph.functions import drawSymbol
from pyqtgraph.graphicsItems.LegendItem import ItemSample

from PySide2.QtCore import QRectF, Signal

from app.plugins.project.visualization.widgets.curve import CurveItem


class _EpureLegendSample(ItemSample):
    """Legend sample that draws both line and scatter proxies."""

    def __init__(self, line_item: pg.PlotDataItem, scatter_item: Optional[pg.ScatterPlotItem]):
        super().__init__(line_item)
        self._scatter_item = scatter_item

    def paint(self, p, *args):
        super().paint(p, *args)

        if self._scatter_item is None:
            return

        symbol = self._scatter_item.opts.get('symbol')

        if symbol in (None, 'None'):
            return

        brush = self._scatter_item.opts.get('brush')
        pen = self._scatter_item.opts.get('pen')
        size = self._scatter_item.opts.get('size', 10)

        if size is None or size <= 0:
            return

        bounds: QRectF = self.boundingRect()

        p.save()
        p.translate(bounds.center())
        drawSymbol(p, symbol, size, pen, brush)
        p.restore()


class LegendProxyPlotDataItem(CurveItem):
    visibilityChanged = Signal(bool)

    def __init__(self, x, y, name="", style=None):
        super().__init__(x, y, name=name, style=style)
        self._isVisible = True  # Трекер текущего состояния видимости

        # Дополнительные прокси-элементы для выборки легенды
        pen = self.opts.get('pen')
        symbol_pen = self.opts.get('symbolPen')
        symbol_brush = self.opts.get('symbolBrush')
        symbol = self.opts.get('symbol')
        symbol_size = self.opts.get('symbolSize')

        self._legend_line_item = pg.PlotDataItem([0, 1], [0, 0], pen=pen)
        self._legend_line_item.setVisible(False)

        if symbol in (None, 'None'):
            self._legend_scatter_item = None
        else:
            self._legend_scatter_item = pg.ScatterPlotItem(
                [0.5],
                [0],
                pen=symbol_pen,
                brush=symbol_brush,
                size=symbol_size,
                symbol=symbol,
            )
            self._legend_scatter_item.setVisible(False)

        # Прячем фактические данные, чтобы прокси не отображались на сцене
        self.setData([], [])
        self.hide()

    def setVisible(self, visible):
        if self._isVisible != visible:  # Проверяем, изменилось ли состояние видимости
            self._isVisible = visible
            super().setVisible(visible)  # Вызываем родительский метод
            self.visibilityChanged.emit(visible)  # Эмитируем сигнал только при изменении

    def legendSample(self, size):
        return _EpureLegendSample(self._legend_line_item, self._legend_scatter_item)
