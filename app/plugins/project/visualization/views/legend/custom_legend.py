from PySide2.QtCore import QEvent
from PySide2.QtGui import QColor, QBrush, QPen
from PySide2.QtWidgets import QMenu
from pyqtgraph import Point
import pyqtgraph as pg

from app import _menu
from app.history_manager.events import LegendPositionChangeEvent
from db import sp
from dialogs.legend_style_dialog import LegendStyleDialog


class CustomLegend(pg.LegendItem):
    """Кастомная легенда с управлением положением и стилем."""

    Z_VALUE_ON_TOP = 1_000_000
    DEFAULT_BACKGROUND = QColor(255, 255, 255)
    DEFAULT_BORDER = QColor(0, 0, 0)
    DEFAULT_OPACITY = 1.0

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self.old_pos = None
        self.last_pos_offset = None  # смещение от начальной точки
        self.current_pos = None  # текущее положение легенды

        self.available_actions = []
        self.legend_menu = self._load_menu('any', 'legend')

        self._background_color = QColor(self.DEFAULT_BACKGROUND)
        self._border_color = QColor(self.DEFAULT_BORDER)
        self._opacity = self.DEFAULT_OPACITY

        self.apply_style()
        self.raise_legend()

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def setOffset(self, offset):
        super().setOffset(offset)
        self.last_pos_offset = Point(offset)
        self.calculate_pos()
        self.raise_legend()

    def event(self, event: QEvent) -> bool:
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
        dialog = LegendStyleDialog(
            background=self._background_color,
            border=self._border_color,
            opacity=self._opacity,
            parent=self._parent
        )

        if dialog.exec_():
            result = dialog.get_result()
            if result:
                self._background_color = QColor(result['background'])
                self._border_color = QColor(result['border'])
                self._opacity = max(0.0, min(1.0, float(result['opacity'])))
                self.apply_style()
                self.raise_legend()

    def apply_style(self):
        """Применяет текущие настройки отображения легенды."""
        background = QColor(self._background_color)
        background.setAlphaF(self._opacity)
        self.setBrush(QBrush(background))
        self.setPen(QPen(self._border_color))

    def raise_legend(self):
        """Выводит легенду поверх остальных элементов сцены."""
        self.setZValue(self.Z_VALUE_ON_TOP)
