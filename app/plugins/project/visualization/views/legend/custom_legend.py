from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QMenu
from pyqtgraph import Point
import pyqtgraph as pg

from app import _menu
from app.history_manager.events import LegendPositionChangeEvent
from app.plugins.project.dialogs.legend_appearance import LegendAppearanceDialog
from app.plugins.project.visualization.views.legend.appearance import LegendAppearance
from db import sp


class CustomLegend(pg.LegendItem):
    """
    Класс легенды

    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self.old_pos = None
        self.last_pos_offset = None  # смещение от начальной точки
        self.current_pos = None  # текущее положение легенды

        self.available_actions = []
        self.legend_menu = self._load_menu('any', 'legend')

        self._appearance = LegendAppearance.default()
        self.apply_appearance(self._appearance)
        self.setZValue(1000)

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def setOffset(self, offset):
        super().setOffset(offset)
        self.last_pos_offset = Point(offset)
        self.calculate_pos()

    def event(self, event: QEvent) -> bool:
        if (event.type() == QEvent.UngrabMouse and self._parent is not None
                and hasattr(self._parent, 'main_window') and hasattr(self._parent.main_window, 'event_stack')):
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
        parent = self._parent if self._parent is not None else None
        dialog = LegendAppearanceDialog(self._appearance, parent)
        if dialog.exec_():
            result = dialog.get_result()
            if result is not None:
                self.apply_appearance(result)

    def apply_appearance(self, appearance: LegendAppearance):
        self._appearance = appearance
        self.setBrush(appearance.to_brush())
        self.setPen(appearance.to_pen())

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.RightButton:
            self.edit_legend(ev.pos())
            ev.accept()
            return
        super().mousePressEvent(ev)
