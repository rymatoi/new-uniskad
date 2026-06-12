import numpy as np
from typing import Optional
import pyqtgraph as pg
from PySide2.QtCore import Qt

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.colors import safe_color


class CurveItem(pg.PlotDataItem):
    def __init__(self, x, y, name="", style=None):
        # Подготовка данных
        self.original_data = (
            np.array(x) if x is not None else None,
            np.array(y) if y is not None else None
        )

        # Применяем стиль по умолчанию если не указан
        base_style = style or GraphConstants.DEFAULT_STYLE
        self._style_config = base_style.copy()
        
        # Для кастомных кривых
        self.custom_curve_id = None

        # Инициализация базового класса
        super().__init__(x, y, name=name)

        # Применяем стиль
        self.apply_style()

    @property
    def style_config(self): #TODO поправить удвоение
        return self._style_config

    @property
    def style(self):
        return self._style_config

    @staticmethod
    def _convert_color(color):
        """Преобразует входное значение в QColor с безопасным fallback."""
        return safe_color(color, '#000000', allow_transparent=True)

    def apply_style(self):
        """Применение стиля к кривой"""
        # Преобразование цвета
        color = self._convert_color(self.style_config.get('color'))

        # Определяем стиль линии
        pen_style = GraphConstants.resolve_pen_style(self.style_config.get('line_style'))
        
        # Установка цвета и стиля линии
        self.setPen(
            color=color,
            width=int(self.style_config.get('width', GraphConstants.DEFAULT_STYLE['width'])),
            style=pen_style
        )

        # Установка символов точек
        self.setSymbol(self.style_config.get('symbol'))
        self.setSymbolSize(int(self.style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size'])))

        # Цвет обводки символа
        symbol_color = self._convert_color(self.style_config.get('symbol_color', color))
        if symbol_color is not None:
            self.setSymbolPen(symbol_color)

        # Установка цвета заливки символов
        if 'fill_color' in self.style_config:
            fill_color = self._convert_color(self.style_config.get('fill_color', symbol_color))
            if fill_color is not None:
                self.setSymbolBrush(fill_color)
            else:
                self.setSymbolBrush(None)
        else:
            self.setSymbolBrush(symbol_color)

    def apply_multipliers(self, x_mul: float, x_div: float, y_mul: float, y_div: float):
        """Применяет множители к данным кривой"""
        if self.original_data[0] is None or self.original_data[1] is None:
            return

        x_data = self.original_data[0] * x_mul / x_div
        y_data = self.original_data[1] * y_mul / y_div

        # Обновляем данные с сохранением текущего стиля
        self.setData(x=x_data, y=y_data)
        self.apply_style()  # Переприменяем стиль после обновления данных

    @property
    def point_size(self):
        return self.style_config['symbol_size']

    @property
    def selected_curve_point_size(self):
        return 0.5  # TODO: Сделать настраиваемым
