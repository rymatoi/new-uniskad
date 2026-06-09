import numpy as np
from typing import Optional
import pyqtgraph as pg
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from app.plugins.project.core.constants import GraphConstants

# Словарь с RGB значениями для именованных цветов
NAMED_COLORS = {
    'Red': '#ff0000',
    'Green': '#00ff00',
    'Blue': '#0000ff',
    'Cyan': '#00ffff',
    'Magenta': '#ff00ff',
    'Yellow': '#ffff00',
    'DarkRed': '#800000',
    'DarkGreen': '#008000',
    'DarkBlue': '#000080',
    'DarkCyan': '#008080',
    'DarkMagenta': '#800080',
    'DarkYellow': '#808000',
    'DarkGray': '#808080',
    'Gray': '#a0a0a4',
    'LightGray': '#c0c0c0',
}

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

    def _convert_color(self, color):
        """Преобразует входное значение в QColor"""
        if color is None:
            return QColor(Qt.GlobalColor.black)

        if isinstance(color, QColor):
            return color

        if isinstance(color, (tuple, list)) and len(color) >= 3:
            return QColor(*color[:3])

        if isinstance(color, str):
            if color.lower() in {'none', 'transparent'}:
                return None
            # Если это именованный цвет из нашего словаря
            if color in NAMED_COLORS:
                return QColor(NAMED_COLORS[color])
            # Если это hex-код цвета
            if color.startswith('#'):
                return QColor(color)
            # Пробуем использовать стандартные цвета Qt или выражения вида rgb()
            qt_color = QColor(color)
            if qt_color.isValid():
                return qt_color
            try:
                return QColor(getattr(Qt, color))
            except AttributeError:
                print(f"Не удалось преобразовать цвет {color}, используем черный")
                return QColor(Qt.GlobalColor.black)

        # На случай неожиданных типов
        qt_color = QColor(color)
        if qt_color.isValid():
            return qt_color
        return QColor(Qt.GlobalColor.black)

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
