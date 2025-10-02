import time

import pyqtgraph as pg
from PySide2 import QtCore, QtGui

from app.plugins.project.visualization.views.legend.custom_legend import CustomLegend


class FPSPlotWidget(pg.PlotWidget):
    """Оболочка для трекинга производительности PlotWidget"""
    display_fps = False

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Инициализация переменных для подсчета FPS
        self.fps = 0
        self.frame_count = 0

        if FPSPlotWidget.display_fps:
            self.start_time = time.perf_counter()

            # Таймер для обновления FPS каждую секунду
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_fps)
            self.timer.start(1000)

    def update_fps(self):
        """Обновление значения FPS"""
        elapsed_time = time.perf_counter() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
        self.frame_count = 0
        self.start_time = time.perf_counter()

    def paintEvent(self, event):
        """Перехват события рисования для подсчета FPS и отображения текста"""
        super().paintEvent(event)
        if FPSPlotWidget.display_fps:
            # Увеличиваем счетчик кадров
            self.frame_count += 1

            # Отображение FPS на виджете
            painter = QtGui.QPainter(self.viewport())
            font = painter.font()
            font.setPointSize(12)  # Размер шрифта
            painter.setFont(font)
            painter.setPen(QtGui.QColor(0, 0, 0))  # Белый цвет текста
            painter.drawText(10, 20, f"FPS: {self.fps:.1f}")  # Позиция текста (x, y)

    def addLegend(self, offset=(30, 30), **kwargs):
        """Создаёт или возвращает легенду, гарантируя использование кастомного класса."""
        legend = getattr(self.plotItem, 'legend', None)
        if legend is not None and not isinstance(legend, CustomLegend):
            if legend.scene() is not None:
                legend.scene().removeItem(legend)
            legend = None

        if not isinstance(legend, CustomLegend):
            legend = CustomLegend(parent=self, offset=offset, **kwargs)
            legend.setParentItem(self.plotItem.vb)
            self.plotItem.legend = legend
        else:
            legend.setOffset(offset)

        legend.raise_legend()
        legend.setVisible(True)
        return legend
