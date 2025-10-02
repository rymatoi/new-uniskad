import PySide2
from PySide2.QtCore import QEvent, Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QDialog, QMenu
from pyqtgraph import Point
import pyqtgraph as pg

from app import _menu
from app.history_manager.events import LegendPositionChangeEvent
from db import sp

from .legend_settings_dialog import LegendSettingsDialog


class CustomLegend(pg.LegendItem):
    """
    Класс легенды

    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self.old_pos = None
        offset = kwargs.get('offset', (30, 30))
        self.last_pos_offset = Point(offset)  # смещение от начальной точки
        self.current_pos = None  # текущее положение легенды

        self.available_actions = []
        self.legend_menu = self._load_menu('any', 'legend')

        self._background_color = QColor(Qt.white)
        self._border_color = QColor(100, 100, 100)
        self._background_opacity = 1.0

        self.setZValue(10_000)
        self._apply_style()

    def open_settings_dialog(self):
        """Открывает диалог настроек легенды."""
        self.edit_legend(None)

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

        if '_edit_legend' not in self.available_actions:
            action = menu.addAction("Настройка легенды…")
            action.triggered.connect(lambda: self.edit_legend(pos))

        return menu

    def connect_triggered_funcs(self, pos):
        self._connect_func('_edit_legend', self.edit_legend, pos)

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def edit_legend(self, pos):
        dialog = LegendSettingsDialog(
            background_color=self._background_color,
            border_color=self._border_color,
            background_opacity=self._background_opacity,
            parent=self._parent
        )

        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_result()
            if not result:
                return

            self.set_background_color(result['background_color'])
            self.set_border_color(result['border_color'])
            self.set_background_opacity(result['background_opacity'])

    def _apply_style(self):
        background = QColor(self._background_color)
        background.setAlpha(int(round(self._background_opacity * 255)))
        self.setBrush(pg.mkBrush(background))

        border = QColor(self._border_color)
        self.setPen(pg.mkPen(border))

    def set_background_color(self, color):
        if color is None:
            return

        self._background_color = QColor(color)
        self._background_color.setAlpha(255)
        self._apply_style()

    def set_border_color(self, color):
        if color is None:
            return

        self._border_color = QColor(color)
        self._border_color.setAlpha(255)
        self._apply_style()

    def set_background_opacity(self, opacity):
        try:
            opacity_value = float(opacity)
        except (TypeError, ValueError):
            return

        self._background_opacity = min(1.0, max(0.0, opacity_value))
        self._apply_style()
