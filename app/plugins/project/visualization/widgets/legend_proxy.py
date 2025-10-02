from PySide2.QtCore import Signal

import pyqtgraph as pg

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.curve import CurveItem


class LegendProxyPlotDataItem(CurveItem):
    visibilityChanged = Signal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isVisible = True  # Трекер текущего состояния видимости
        self._ensure_legend_opts()

    def setVisible(self, visible):
        if self._isVisible != visible:  # Проверяем, изменилось ли состояние видимости
            self._isVisible = visible
            super().setVisible(visible)  # Вызываем родительский метод
            self.visibilityChanged.emit(visible)  # Эмитируем сигнал только при изменении

    def apply_style(self):
        super().apply_style()
        self._ensure_legend_opts()

    def setPen(self, *args, **kwargs):
        super().setPen(*args, **kwargs)
        self._ensure_legend_opts()

    def setSymbol(self, *args, **kwargs):
        super().setSymbol(*args, **kwargs)
        self._ensure_legend_opts()

    def setSymbolSize(self, *args, **kwargs):
        super().setSymbolSize(*args, **kwargs)
        self._ensure_legend_opts()

    def setSymbolPen(self, *args, **kwargs):
        super().setSymbolPen(*args, **kwargs)
        self._ensure_legend_opts()

    def setSymbolBrush(self, *args, **kwargs):
        super().setSymbolBrush(*args, **kwargs)
        self._ensure_legend_opts()

    def refresh_legend_opts(self):
        """Публичный метод для принудительного обновления настроек легенды."""
        self._ensure_legend_opts()

    def _ensure_legend_opts(self):
        """Гарантирует наличие настроек, необходимых для отрисовки элемента в легенде."""
        style = self.style_config
        defaults = GraphConstants.DEFAULT_STYLE

        symbol_size = int(style.get('symbol_size', defaults['symbol_size']))
        self.opts['size'] = symbol_size

        symbol = style.get('symbol', defaults['symbol'])
        if symbol is not None:
            self.opts['symbol'] = symbol

        def normalize_color(value, fallback):
            if value is None:
                return fallback
            if isinstance(value, str) and value.lower() in {'none', 'transparent'}:
                return None
            return value

        # Pen for the curve line in the legend sample
        pen_color_value = normalize_color(style.get('color'), defaults['color'])
        pen_color = self._convert_color(pen_color_value)
        pen_width = int(style.get('width', defaults['width']))
        pen_style = GraphConstants.resolve_pen_style(style.get('line_style'))
        self.opts['pen'] = pg.mkPen(color=pen_color, width=pen_width, style=pen_style)

        # Symbol outline color
        symbol_color_value = normalize_color(style.get('symbol_color'), pen_color_value)
        symbol_color = self._convert_color(symbol_color_value) if symbol_color_value is not None else None
        self.opts['symbolPen'] = pg.mkPen(symbol_color) if symbol_color is not None else pg.mkPen(None)

        # Symbol fill color and compatibility brush entry
        fill_color_setting = normalize_color(style.get('fill_color'), symbol_color_value)
        fill_color = self._convert_color(fill_color_setting) if fill_color_setting is not None else None
        brush = pg.mkBrush(fill_color) if fill_color is not None else pg.mkBrush(None)
        self.opts['symbolBrush'] = brush
        # LegendItem.paint expects a generic 'brush' key for scatter-only samples
        self.opts['brush'] = brush
