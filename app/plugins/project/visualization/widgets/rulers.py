from typing import TYPE_CHECKING

import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import Qt
from PySide2.QtCore import QPointF

if TYPE_CHECKING:
    from typing import Optional


class Ruler:
    """Линейка для измерения расстояния между кривыми."""

    def __init__(self, parent: "pg.PlotItem", enabled: bool = False):
        self.parent: "pg.PlotItem" = parent
        self.enabled: bool = enabled
        self._pos: "Optional[QPointF]" = None
        self._line = pg.InfiniteLine(
            angle=90,
            movable=True,
            pen=pg.mkPen((0, 0, 0), width=1, style=Qt.SolidLine),
        )

        self._label = pg.InfLineLabel(
            self._line,
            text="Δy",
            movable=True,
            position=0.1,
            color=(0, 0, 0),
        )

        self._delta_line = pg.PlotDataItem(parent=parent)

        self._curve1 = None
        self._curve2 = None
        self.last_pos = None

        self._line.setVisible(False)
        self._create_connections()

    def _create_connections(self):
        self._line.sigPositionChanged.connect(self.update)

    def add(self):
        """
        Добавление линейки на график
        """
        self.parent.addItem(self._line, ignoreBounds=True)
        self.parent.addItem(self._delta_line)
        self.enabled = True
        self._line.setVisible(True)

    def remove(self):
        """
        Удалвние линейки с графика
        """
        self.parent.removeItem(self._line)
        self.parent.removeItem(self._delta_line)
        self.enabled = False
        self._line.setVisible(False)

    @classmethod
    def _y_pos(cls, x_pos: "float", curve: "pg.PlotCurveItem") -> "float":
        """Найти значение функции в точке ``x_pos`` для кривой ``curve``."""
        if curve:
            y_pos = np.interp(x_pos, curve.xData, curve.yData)
            if curve.curve.mouseShape().contains(QPointF(x_pos, y_pos)):
                return y_pos
        return None

    def update(self):
        """
        Перемещение/обновление таблички с данными линейки
        """
        x_pos = self._line.pos().x()
        y1_pos = self._y_pos(x_pos, self._curve1)
        y2_pos = self._y_pos(x_pos, self._curve2)

        if y1_pos is None and y2_pos is None:
            y1 = y2 = 0
        else:
            y1 = y2_pos if y1_pos is None else y1_pos
            y2 = y1_pos if y2_pos is None else y2_pos
        self.last_pos = (x_pos, y1 if y1 else y2)

        dy = abs(y2 - y1)

        if self._curve1:
            curve1_name = self._curve1.scatter.name() if self._curve1 else self._curve2.scatter.name()
        else:
            curve1_name = '-'
        if self._curve2:
            curve2_name = self._curve2.scatter.name() if self._curve2 else self._curve1.scatter.name()
        else:
            curve2_name = '-'

        self._label.setText(
            f"y1 = {curve1_name}\n"
            f"y2 = {curve2_name}\n"
            f"Δy={dy} \ny1/y2={float(float(y1) / float(y2)) if y2 else 'inf'} \n"
            f"y ср.={float((float(y1) + float(y2)) / 2)}")

        self._delta_line.setData([x_pos, x_pos], [y1, y2],
                                 symbolSize=10 if (y1_pos is not None or y2_pos is not None) else 0)
        self._delta_line.setPen(color=(255, 0, 0), width=2)

    def set_pos(self, pos, curve=None):
        """
        Прикрепление линейки к кривым
        """
        if not self._curve1:
            self._curve1 = curve
            self._line.setPos(pos)
            if not self.enabled:
                self.add()
        else:
            if self._curve1 == curve:
                if self._curve2:
                    self._curve1 = self._curve2
                    self._curve2 = None
                else:
                    self._curve1 = None
                    self.remove()
            else:
                if not self._curve2:
                    self._curve2 = curve
                    self._line.setPos(pos)
                else:
                    self._curve2 = None
                    self._line.setPos(self.last_pos)
        self.update()
