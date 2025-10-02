from PySide2.QtCore import Signal

import pyqtgraph as pg

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.curve import CurveItem


class LegendProxyPlotDataItem(CurveItem):
    visibilityChanged = Signal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isVisible = True  # Трекер текущего состояния видимости
        self._sync_legend_opts()

    def setVisible(self, visible):
        if self._isVisible != visible:  # Проверяем, изменилось ли состояние видимости
            self._isVisible = visible
            super().setVisible(visible)  # Вызываем родительский метод
            self.visibilityChanged.emit(visible)  # Эмитируем сигнал только при изменении

    def apply_style(self):
        super().apply_style()
        self._sync_legend_opts()

    def update_style(self, style: dict | None = None):
        """Обновляет конфигурацию стиля и синхронизирует настройки легенды."""
        if style:
            self._style_config.update(style)
        self.apply_style()

    def refresh_legend_opts(self):
        """Публичный метод для принудительного обновления настроек легенды."""
        self._sync_legend_opts()

    def _sync_legend_opts(self):
        """Заполняет параметры, необходимые легенде PyQtGraph."""
        defaults = GraphConstants.DEFAULT_STYLE
        style = defaults.copy()
        style.update({k: v for k, v in self.style_config.items() if v is not None})

        symbol_size = int(style.get('symbol_size', defaults['symbol_size']))
        symbol = style.get('symbol', defaults['symbol'])

        pen_color = self._convert_color(style.get('color', defaults['color']))
        pen_width = int(style.get('width', defaults['width']))
        pen_style = GraphConstants.resolve_pen_style(style.get('line_style'))
        pen = pg.mkPen(color=pen_color, width=pen_width, style=pen_style)

        symbol_color_value = style.get('symbol_color', style.get('color', defaults['color']))
        symbol_color = None if symbol_color_value is None else self._convert_color(symbol_color_value)
        symbol_pen = pg.mkPen(symbol_color) if symbol_color is not None else pg.mkPen(None)

        fill_color_value = style.get('fill_color', symbol_color_value)
        fill_color = None if fill_color_value is None else self._convert_color(fill_color_value)
        brush = pg.mkBrush(fill_color) if fill_color is not None else pg.mkBrush(None)

        # Синхронизируем визуальные параметры элемента
        self.setPen(pen)
        self.setSymbol(symbol)
        self.setSymbolSize(symbol_size)
        self.setSymbolPen(symbol_pen)
        self.setSymbolBrush(brush)

        # PyQtGraph ожидает дополнительные ключи для корректного рендера легенды
        self.opts.update({
            'pen': pen,
            'symbol': symbol,
            'size': symbol_size,
            'symbolPen': symbol_pen,
            'symbolBrush': brush,
            'brush': brush,
        })
