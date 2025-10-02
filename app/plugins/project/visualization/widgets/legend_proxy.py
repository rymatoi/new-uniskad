from PySide2.QtCore import Signal

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

    def _ensure_legend_opts(self):
        """Гарантирует наличие настроек, необходимых для отрисовки элемента в легенде."""
        # В LegendItem.paint ожидается ключ "size". У PlotDataItem он появляется только для
        # ScatterPlotItem, поэтому добавляем его вручную, чтобы избежать KeyError.
        symbol_size = int(self.style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size']))
        self.opts['size'] = symbol_size

        # Также явно сохраняем текущий символ, так как он может быть задан позже через стиль.
        symbol = self.style_config.get('symbol', GraphConstants.DEFAULT_STYLE['symbol'])
        if symbol is not None:
            self.opts['symbol'] = symbol
