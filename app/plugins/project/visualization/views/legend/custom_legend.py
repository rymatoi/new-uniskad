import PySide2
from PySide2.QtCore import QEvent
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QMenu
from pyqtgraph import Point
import pyqtgraph as pg

from app import _menu
from app.history_manager.events import LegendPositionChangeEvent
from db import sp

from app.plugins.project.dialogs.legend_style import LegendStyleDialog


class CustomLegend(pg.LegendItem):
    """
    Класс легенды

    """

    def __init__(self, parent=None, *args, **kwargs):
        offset = kwargs.get('offset', (0, 0))
        super().__init__(*args, **kwargs)
        self._parent = parent
        self.old_pos = None
        self.last_pos_offset = Point(offset)  # смещение от начальной точки
        self.current_pos = None  # текущее положение легенды

        self._background_color = QColor(255, 255, 255)
        self._border_color = QColor(100, 100, 100)
        self._opacity = 1.0

        self.available_actions = []
        self.legend_menu = self._load_menu('any', 'legend')

        self._apply_style_settings()

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def setOffset(self, offset):
        super().setOffset(offset)
        self.last_pos_offset = Point(offset)
        self.calculate_pos()

    def event(self, event: PySide2.QtCore.QEvent) -> bool:
        if event.type() == QEvent.UngrabMouse:
            self._parent.main_window.event_stack.add_event(
                LegendPositionChangeEvent(self, self.old_pos, self.current_pos))
        return super().event(event)

    def mouseDragEvent(self, ev):
        """
        Перемещение легенды, просчитывает новое положение
        """
        super().mouseDragEvent(ev)

        self.calculate_pos()
        self.last_pos_offset += ev.pos() - ev.lastPos()

    def calculate_pos(self):
        anchorx = 1 if self.last_pos_offset.x() <= 0 else 0
        anchory = 1 if self.last_pos_offset.y() <= 0 else 0
        anchor = (anchorx, anchory)

        o = self.mapToParent(Point(0, 0))
        a = self.boundingRect().bottomRight() * Point(anchor)
        a = self.mapToParent(a)
        p = self.parentItem().boundingRect().bottomRight() * Point(anchor)
        off = Point(self.last_pos_offset)

        self.old_pos = self.current_pos
        self.current_pos = p + (o - a) + off

    def update_pos(self, pos):
        if pos is not None:
            self.setOffset(pos)

    def on_context_menu(self, pos):
        pass
        # menu = self.menu(pos)
        # menu.exec_(QCursor.pos())

    def menu(self, pos):
        menu = QMenu(self.getViewWidget())
        _menu.init_menu(self.legend_menu, self, menu)
        self.connect_triggered_funcs(pos)
        return menu

    def connect_triggered_funcs(self, pos):
        self._connect_func('_edit_legend', self.edit_legend, pos)

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def edit_legend(self, pos):
        dialog = LegendStyleDialog(self, parent=self.getViewWidget())
        if dialog.exec_():
            background_color, border_color, opacity = dialog.get_values()
            self.apply_style_settings(background_color=background_color,
                                      border_color=border_color,
                                      opacity=opacity)

    @property
    def background_color(self) -> QColor:
        return QColor(self._background_color)

    @property
    def border_color(self) -> QColor:
        return QColor(self._border_color)

    @property
    def opacity(self) -> float:
        return float(self._opacity)

    def apply_style_settings(self, background_color: QColor = None,
                              border_color: QColor = None,
                              opacity: float = None):
        if background_color is not None:
            self._background_color = QColor(background_color)
        if border_color is not None:
            self._border_color = QColor(border_color)
        if opacity is not None:
            self._opacity = max(0.0, min(1.0, float(opacity)))

        self._apply_style_settings()

    def _apply_style_settings(self):
        brush_color = QColor(self._background_color)
        brush_color.setAlphaF(self._opacity)
        self.setBrush(pg.mkBrush(brush_color))
        self.setPen(pg.mkPen(self._border_color))
