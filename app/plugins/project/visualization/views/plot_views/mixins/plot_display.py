from typing import TYPE_CHECKING, cast, Any, Tuple, Dict, Callable, Optional

import pyqtgraph as pg
from PySide2.QtGui import QSurfaceFormat
from pyqtgraph import PlotWidget

from app.basic_funcs import to_bool
from app.plugins.project.plot.ruler import Ruler
from app.plugins.project.services.data_processors.base_dp import DataProcessor
from app.plugins.project.services.data_processors.plot_dp import PlotProcessor


class PlotDisplayMixin:
    """Миксин для управления отображением графика"""

    # Внешние атрибуты и методы
    plotItem: Any
    item: Any
    data_processor: PlotProcessor
    sceneObj: Any
    setBackground: Callable
    showGrid: Callable
    setLabel: Callable
    setAntialiasing: Callable
    setXRange: Callable
    setYRange: Callable
    getAxis: Callable
    addLegend: Callable
    enableAutoRange: Callable

    def __init__(self):
        self._display_settings: dict = {
            'x_range': (None, None),
            'y_range': (None, None),
            'x_fixed': False,
            'y_fixed': False,
            'x_multiplier': 1.0,
            'y_multiplier': 1.0,
            'x_divider': 1.0,
            'y_divider': 1.0,
            'grid_settings': {
                'x': {'major': None, 'minor': None, 'auto': True},
                'y': {'major': None, 'minor': None, 'auto': True}
            }
        }

        self.init_view()

    def init_legend(self):
        self.addLegend()

    @property
    def legend(self):
        return self.plotItem.legend

    def _fix_performance(self):
        """Оптимизация производительности"""
        self.setAntialiasing(False)
        self.sceneObj.setItemIndexMethod(pg.GraphicsScene.BspTreeIndex)
        fmt = QSurfaceFormat()
        fmt.setSwapInterval(0)
        QSurfaceFormat.setDefaultFormat(fmt)
        pg.setConfigOptions(useOpenGL=False)

    def init_view(self):
        """Инициализация базовых параметров отображения"""
        self._fix_performance()
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('left', self.item.graph_label_x)
        self.setLabel('bottom', self.item.graph_label_y)
        self.plotItem.setMenuEnabled(False)

    def update_display_settings_from_item(self):
        """Обновление настроек отображения из item"""
        if hasattr(self.item, 'graph_left_x'):
            self._display_settings['x_range'] = (
                float(self.item.graph_left_x) if self.item.graph_left_x else None,
                float(self.item.graph_right_x) if self.item.graph_right_x else None
            )
        if hasattr(self.item, 'graph_bottom_y'):
            self._display_settings['y_range'] = (
                float(self.item.graph_bottom_y) if self.item.graph_bottom_y else None,
                float(self.item.graph_top_y) if self.item.graph_top_y else None
            )

        self._display_settings.update({
            'x_fixed': to_bool(getattr(self.item, 'graph_fixed_x', False)),
            'y_fixed': to_bool(getattr(self.item, 'graph_fixed_y', False)),
            'x_multiplier': float(getattr(self.item, 'graph_x_multiplier', 1.0)),
            'y_multiplier': float(getattr(self.item, 'graph_y_multiplier', 1.0)),
            'x_divider': float(getattr(self.item, 'graph_x_dultiplier', 1.0)),
            'y_divider': float(getattr(self.item, 'graph_y_dultiplier', 1.0))
        })

        self._apply_display_settings()

    def _apply_display_settings(self):
        """Применение настроек отображения"""
        # Сохраняем видимость линеек
        ruler_visibility = {}
        
        # Новый формат с несколькими линейками
        if hasattr(self, 'rulers'):
            for ruler_id, ruler in self.rulers.items():
                if hasattr(ruler, 'line') and hasattr(ruler.line, 'isVisible'):
                    ruler_visibility[ruler_id] = ruler.line.isVisible()
        # Старый формат с одной линейкой
        elif hasattr(self, 'ruler_line') and hasattr(self.ruler_line, 'isVisible'):
            ruler_visibility['old'] = self.ruler_line.isVisible()
            
        if self._display_settings['x_fixed']:
            self.setXRange(*self._display_settings['x_range'])
        if self._display_settings['y_fixed']:
            self.setYRange(*self._display_settings['y_range'])

        grid_settings = self._display_settings['grid_settings']
        for axis in ['x', 'y']:
            if not grid_settings[axis]['auto']:
                axis_item = self.getAxis('bottom' if axis == 'x' else 'left')
                axis_item.setTickSpacing(
                    grid_settings[axis]['major'],
                    grid_settings[axis]['minor']
                )
                
        # Восстанавливаем видимость линеек, если они были активны
        if ruler_visibility:
            # Новый формат с несколькими линейками
            if hasattr(self, 'rulers'):
                for ruler_id, visible in ruler_visibility.items():
                    if visible and ruler_id in self.rulers:
                        ruler = self.rulers[ruler_id]
                        ruler.line.setVisible(True)
                        ruler.delta_line.setVisible(True)
                        print(f"Восстановлена видимость линейки {ruler_id}")
            # Старый формат с одной линейкой
            elif 'old' in ruler_visibility and ruler_visibility['old'] and hasattr(self, 'ruler_line'):
                self.ruler_line.setVisible(True)
                if hasattr(self, 'ruler_delta_line'):
                    self.ruler_delta_line.setVisible(True)
                print("Восстановлена видимость линейки после применения настроек отображения")
            
            # Вызываем метод для вывода линеек на передний план
            if hasattr(self, 'bring_to_front'):
                # Новый формат с несколькими линейками
                if hasattr(self, 'rulers'):
                    for ruler_id, visible in ruler_visibility.items():
                        if visible and ruler_id in self.rulers:
                            self.bring_to_front(ruler_id)
                # Старый формат с одной линейкой
                elif 'old' in ruler_visibility and ruler_visibility['old']:
                    self.bring_to_front()
                print("Линейки выведены на передний план после применения настроек")

    def set_axis_range(self, axis, min_val, max_val):
        """Установка диапазона для оси"""
        if axis.lower() == 'x':
            self._display_settings['x_range'] = (min_val, max_val)
            if self._display_settings['x_fixed']:
                self.setXRange(min_val, max_val)
        elif axis.lower() == 'y':
            self._display_settings['y_range'] = (min_val, max_val)
            if self._display_settings['y_fixed']:
                self.setYRange(min_val, max_val)

    def set_grid_spacing(self, axis, major=None, minor=None, auto=True):
        """Установка интервалов сетки"""
        if axis.lower() not in ['x', 'y']:
            return

        self._display_settings['grid_settings'][axis] = {
            'major': major,
            'minor': minor,
            'auto': auto
        }

        if not auto:
            axis_obj = self.getAxis('bottom' if axis == 'x' else 'left')
            axis_obj.setTickSpacing(major, minor)

    def reset_view(self):
        """Сброс настроек отображения"""
        self.enableAutoRange()
        for settings in self._display_settings['grid_settings'].values():
            settings['auto'] = True
        self.showGrid(x=True, y=True, alpha=0.3)

    def clear(self):
        self.plotItem.clear()
        self.plotItem.legend.clear()

    def refresh(self, test_ids=None) -> None:
        """Обновляет отображение графика
        
        Args:
            test_ids: Список идентификаторов тестов для обновления.
                     Если None, обновляются все кривые.
        """
        # Сохраняем состояние линеек перед обновлением
        rulers_state = None
        if hasattr(self, 'save_rulers_state'):
            rulers_state = self.save_rulers_state()
        elif hasattr(self, 'save_ruler_state'):  # Для обратной совместимости
            rulers_state = self.save_ruler_state()
            
        self._update_curves(test_ids)

        self.update_display_settings_from_item()
        self._apply_display_settings()
        
        # Восстанавливаем состояние линеек после обновления
        if rulers_state:
            if hasattr(self, 'restore_rulers_state'):
                self.restore_rulers_state(rulers_state)
            elif hasattr(self, 'restore_ruler_state'):  # Для обратной совместимости
                self.restore_ruler_state(rulers_state)
            
            # Выводим линейки на передний план
            if hasattr(self, 'bring_to_front'):
                if hasattr(self, 'rulers'):  # Новый формат с несколькими линейками
                    for ruler_id in self.rulers:
                        if self.rulers[ruler_id].enabled:
                            self.bring_to_front(ruler_id)
                elif hasattr(self, 'ruler_enabled') and self.ruler_enabled:  # Старый формат
                    self.bring_to_front()
                    
                print("Все линейки выведены на передний план после восстановления состояния")

    def _update_curves(self, test_ids) -> None:
        """Обновляет кривые на графике
        
        Args:
            test_ids: Список идентификаторов тестов для обновления.
                     Если None, обновляются все кривые.
        """
        if test_ids is None:
            # Полное обновление всех кривых
            self.clear()
            self.prepare_curves()
        else:
            # Обновляем только указанные кривые
            for test_id in test_ids:
                # Удаляем старые кривые для этого test_id
                curves = self.data_processor.get_curves_for_test(test_id)
                for curve in curves:
                    self.remove_curve(curve)

                # Добавляем новые кривые для этого test_id
                for _, x, y, style in self.data_processor.get_curves():
                    if _ == test_id:  # проверяем, что это нужный test_id
                        curve = self.add_curve(x, y, **style)
                        self.data_processor.register_curve(test_id, curve)
