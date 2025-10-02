from PySide2.QtCore import Signal
from app.plugins.project.visualization.widgets.curve import CurveItem


class LegendProxyPlotDataItem(CurveItem):
    visibilityChanged = Signal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isVisible = True  # Трекер текущего состояния видимости
        self.setData([0, 1], [0, 0])

    def setVisible(self, visible):
        if self._isVisible != visible:  # Проверяем, изменилось ли состояние видимости
            self._isVisible = visible
            super().setVisible(visible)  # Вызываем родительский метод
            self.visibilityChanged.emit(visible)  # Эмитируем сигнал только при изменении
