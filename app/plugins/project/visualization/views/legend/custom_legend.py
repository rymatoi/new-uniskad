from typing import Dict

import PySide2
from PySide2.QtCore import QEvent, Qt
from PySide2.QtWidgets import QMenu
from PySide2.QtGui import QColor
from pyqtgraph import Point
import pyqtgraph as pg

from app import _menu
from app.history_manager.events import LegendPositionChangeEvent
from db import sp
from app.plugins.project.dialogs.legend_settings_dialog import LegendSettingsDialog
from app.plugins.project.visualization.views.legend.settings_store import (
    default_legend_settings,
    load_legend_settings,
    normalize_legend_settings,
    save_legend_settings,
)


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
        base_settings = self._collect_settings()
        self._legend_settings = load_legend_settings(base_settings)
        self._background_brush = None
        # Делает легенду поверх остальных элементов графика
        self.setZValue(10_000)
        self._apply_settings()
        self._ensure_last_offset()

    def apply_settings(self, settings: Dict[str, object]) -> Dict[str, object]:
        """Применяет переданные настройки без дополнительного сохранения."""
        self._legend_settings = normalize_legend_settings({**self._legend_settings, **settings})
        self._apply_settings()
        if hasattr(self._parent, "legend_settings"):
            self._parent.legend_settings = self._legend_settings
        return self._legend_settings

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def setOffset(self, offset):
        super().setOffset(offset)
        self.last_pos_offset = self._normalize_offset(offset)
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
        offset = self._ensure_last_offset()
        self.last_pos_offset = offset + (ev.pos() - ev.lastPos())

    def calculate_pos(self):
        offset = self._ensure_last_offset()

        anchorx = 1 if offset.x() <= 0 else 0
        anchory = 1 if offset.y() <= 0 else 0
        anchor = (anchorx, anchory)

        o = self.mapToParent(Point(0, 0))
        a = self.boundingRect().bottomRight() * Point(anchor)
        a = self.mapToParent(a)
        p = self.parentItem().boundingRect().bottomRight() * Point(anchor)
        off = Point(offset)

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
        dialog = LegendSettingsDialog(self._legend_settings, parent=self.getViewWidget())
        if dialog.exec_():
            settings = dialog.get_result()
            if settings:
                merged = {**self._legend_settings, **settings}
                self._legend_settings = save_legend_settings(merged)
                if hasattr(self._parent, "legend_settings"):
                    self._parent.legend_settings = self._legend_settings
                self._apply_settings()

    def _collect_settings(self):
        brush = self.opts.get('brush')
        pen = self.opts.get('pen')

        defaults = default_legend_settings()
        background_color = defaults['background_color']
        opacity = defaults['background_opacity']
        border_color = defaults['border_color']
        border_width = defaults['border_width']

        if brush is not None:
            color = brush.color()
            background_color = QColor(color)
            opacity = int(round(color.alpha() / 255 * 100))

        if pen is not None:
            border_color = QColor(pen.color())
            if pen.style() == Qt.NoPen or pen.width() <= 0:
                border_width = 0
            else:
                border_width = pen.width()

        return {
            'background_color': background_color,
            'background_opacity': opacity,
            'border_color': border_color,
            'border_width': border_width
        }

    def _apply_settings(self):
        self._legend_settings = normalize_legend_settings(self._legend_settings)

        background = QColor(self._legend_settings.get('background_color'))
        opacity_percent = self._legend_settings.get('background_opacity', 100)
        if opacity_percent >= 100:
            alpha = 255
        else:
            alpha = int(round(opacity_percent * 2.55))
        background.setAlpha(alpha)
        self._background_brush = pg.mkBrush(background)
        self.setBrush(self._background_brush)
        self.update()

        border_color = QColor(self._legend_settings.get('border_color'))
        border_width = max(0, int(self._legend_settings.get('border_width', 1)))
        if border_width == 0:
            pen = pg.mkPen(border_color)
            pen.setStyle(Qt.NoPen)
        else:
            pen = pg.mkPen(border_color, width=border_width)
        self.setPen(pen)

    def _normalize_offset(self, offset):
        if offset is None:
            return Point(0, 0)
        try:
            return Point(offset)
        except TypeError:
            try:
                return Point(offset.x(), offset.y())  # type: ignore[attr-defined]
            except Exception:
                return Point(0, 0)

    def _ensure_last_offset(self) -> Point:
        if self.last_pos_offset is None:
            offset = self.opts.get('offset') if hasattr(self, 'opts') else None
            self.last_pos_offset = self._normalize_offset(offset)
        return Point(self.last_pos_offset)

    def paint(self, painter, *args):  # type: ignore[override]
        if self._background_brush is not None:
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._background_brush)
            painter.drawRect(self.boundingRect())
            painter.restore()

        super().paint(painter, *args)
