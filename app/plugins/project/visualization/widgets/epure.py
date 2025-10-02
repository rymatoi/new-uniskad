import numpy as np

from PySide2.QtCore import Qt
import pyqtgraph as pg

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.legend_proxy import LegendProxyPlotDataItem


class EpureItem(pg.ItemGroup):
    def __init__(self, all_scatter_data, all_plot_data, **kwargs):
        super().__init__()

        self._style_config = kwargs.get('style', GraphConstants.DEFAULT_STYLE.copy()).copy()
        if 'symbol_size' not in self._style_config:
            self._style_config['symbol_size'] = GraphConstants.DEFAULT_STYLE['symbol_size']
        if 'color' not in self._style_config:
            self._style_config['color'] = GraphConstants.DEFAULT_STYLE['color']
        if 'fill_color' not in self._style_config:
            self._style_config['fill_color'] = self._style_config['color']
        if 'width' not in self._style_config:
            self._style_config['width'] = GraphConstants.DEFAULT_STYLE['width']
        if 'symbol' not in self._style_config:
            self._style_config['symbol'] = GraphConstants.DEFAULT_STYLE['symbol']
        if 'symbol_color' not in self._style_config:
            self._style_config['symbol_color'] = self._style_config['color']

        # Линия эпюры должна быть видимой независимо от исходного стиля
        resolved_pen_style = GraphConstants.resolve_pen_style(self._style_config.get('line_style'))
        if resolved_pen_style == Qt.NoPen:
            self._style_config['line_style'] = GraphConstants.DEFAULT_STYLE['line_style']

        width_value = self._style_config.get('width', GraphConstants.DEFAULT_STYLE['width'])
        try:
            width_value = int(width_value)
        except (TypeError, ValueError):
            width_value = GraphConstants.DEFAULT_STYLE['width']
        if width_value <= 0:
            width_value = GraphConstants.DEFAULT_STYLE['width']
        self._style_config['width'] = width_value
        self._name = self._style_config.get('name', 'Epure')

        # Прокси-элемент для легенды (невидимый на графике)
        self.legend_proxy = self.init_legend_proxy()

        scatter_pairs = [
            (np.asarray(x, dtype=float), np.asarray(y, dtype=float))
            for x, y in all_scatter_data
        ]

        if scatter_pairs:
            scatter_x = np.concatenate([pair[0] for pair in scatter_pairs])
            scatter_y = np.concatenate([pair[1] for pair in scatter_pairs])
        else:
            scatter_x = np.empty(0, dtype=float)
            scatter_y = np.empty(0, dtype=float)

        curve_pairs = [
            (np.asarray(x, dtype=float), np.asarray(y, dtype=float))
            for x, y in all_plot_data
        ]

        if curve_pairs:
            total_points = sum(pair[0].size for pair in curve_pairs)
            gap_count = max(len(curve_pairs) - 1, 0)

            x_arr = np.empty(total_points + gap_count, dtype=float)
            y_arr = np.empty(total_points + gap_count, dtype=float)

            position = 0
            for index, (x_data, y_data) in enumerate(curve_pairs):
                length = x_data.size
                if length:
                    x_arr[position:position + length] = x_data
                    y_arr[position:position + length] = y_data
                    position += length

                if index < len(curve_pairs) - 1:
                    x_arr[position] = np.nan
                    y_arr[position] = np.nan
                    position += 1

            if position < x_arr.size:
                x_arr = x_arr[:position]
                y_arr = y_arr[:position]
        else:
            x_arr = np.empty(0, dtype=float)
            y_arr = np.empty(0, dtype=float)

        # Создаем один scatter для всех исходных точек
        self.scatter = self._create_scatter((scatter_x, scatter_y))
        # Создаем одну кривую для всех интерполированных сегментов
        self.curve = self._create_curve((x_arr, y_arr))

        # Добавляем элементы в обратном порядке, чтобы точки были поверх линий
        self.addItem(self.curve)
        self.addItem(self.scatter)

        # Синхронизация видимости
        self.legend_proxy.visibilityChanged.connect(self.set_visible)

    @property
    def style_config(self):
        return self._style_config

    def init_legend_proxy(self):
        legend_proxy = LegendProxyPlotDataItem([], [], name=self._name, style=self._style_config)
        legend_proxy.setVisible(True)

        symbol_pen_width = self._style_config.get('symbol_pen_width', 1)
        try:
            symbol_pen_width = int(symbol_pen_width)
        except (TypeError, ValueError):
            symbol_pen_width = 1
        symbol_pen_width = max(1, symbol_pen_width)

        symbol = self._style_config.get('symbol', GraphConstants.DEFAULT_STYLE['symbol'])
        symbol_size = self._style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size'])
        line_pen = pg.mkPen(
            color=self._style_config['color'],
            style=GraphConstants.resolve_pen_style(self._style_config.get('line_style')),
            width=self._style_config.get('width', GraphConstants.DEFAULT_STYLE['width'])
        )
        symbol_brush = pg.mkBrush(self._style_config['fill_color'])
        symbol_pen = pg.mkPen(
            self._style_config.get('symbol_color', self._style_config['color']),
            width=symbol_pen_width
        )

        legend_proxy.opts.update({
            'size': symbol_size,
            'pen': line_pen,
            'brush': symbol_brush,
            'symbol': symbol,
            'symbolBrush': symbol_brush,
            'symbolPen': symbol_pen
        })

        # Используем фиктивные данные и явные настройки, чтобы легенда отображала и линию, и точку
        legend_proxy.setData([0, 1], [0, 0])
        legend_proxy.setPen(line_pen)
        legend_proxy.setBrush(symbol_brush)
        legend_proxy.setSymbol(symbol)
        legend_proxy.setSymbolSize(symbol_size)
        legend_proxy.setSymbolBrush(symbol_brush)
        legend_proxy.setSymbolPen(symbol_pen)
        return legend_proxy

    def _create_curve(self, plot_data):
        x, y = plot_data
        return pg.PlotCurveItem(
            x=x,
            y=y,
            connect='finite',
            pen=pg.mkPen(
                color=self._style_config['color'],
                width=self._style_config.get('width', 2),
                style=GraphConstants.resolve_pen_style(self._style_config.get('line_style'))
            )
        )

    def _create_scatter(self, scatter_data):
        x, y = scatter_data
        return pg.ScatterPlotItem(
            x=x,
            y=y,
            symbol=self._style_config['symbol'],
            size=self._style_config.get('symbol_size', 8),
            brush=pg.mkBrush(self._style_config['fill_color']),
            pen=pg.mkPen(color=self._style_config.get('symbol_color', self._style_config['color']))
        )

    @property
    def opts(self):
        return self.legend_proxy.opts

    @property
    def point_size(self):
        return self.style_config['symbol_size']

    @property
    def selected_curve_point_size(self):
        return 0.5  # TODO: Сделать настраиваемым

    def name(self):
        return self._name

    def implements(self, interface=None):
        ints = ['plotData']
        if interface is None:
            return ints
        return interface in ints

    def set_visible(self, visible):
        """Переопределение видимости для всей группы"""
        self.setVisible(visible)
        self.legend_proxy.setVisible(visible)
        # Явно устанавливаем видимость для подэлементов
        if self.curve:
            self.curve.setVisible(visible)
        if self.scatter:
            self.scatter.setVisible(visible)

    def dataBounds(self, axis, frac=1.0, orthoRange=None):
        """Для корректного авто-масштабирования"""
        bounds = [None, None]
        for item in [self.curve, self.scatter]:
            b = item.dataBounds(axis, frac, orthoRange)
            if b[0] is not None:
                bounds[0] = b[0] if bounds[0] is None else min(bounds[0], b[0])
            if b[1] is not None:
                bounds[1] = b[1] if bounds[1] is None else max(bounds[1], b[1])
        return bounds
