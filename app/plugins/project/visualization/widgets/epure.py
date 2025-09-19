import numpy as np
from PySide2.QtWidgets import QGraphicsItem

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.legend_proxy import LegendProxyPlotDataItem
import pyqtgraph as pg


class EpureItem(pg.ItemGroup):
    def __init__(self, all_scatter_data, all_plot_data, **kwargs):
        super().__init__()

        self._style_config = kwargs.get('style', GraphConstants.DEFAULT_STYLE.copy())
        self._name = self._style_config.get('name', 'Epure')

        # Прокси-элемент для легенды (невидимый на графике)
        self.legend_proxy = self.init_legend_proxy()

        # Объединяем все точки в один массив
        scatter_x = []
        scatter_y = []
        for _, scatter_data in zip(all_plot_data, all_scatter_data):
            x, y = scatter_data
            scatter_x.extend(x)
            scatter_y.extend(y)

        # Объединяем все интерполированные кривые в один массив
        plot_segments_x = []
        plot_segments_y = []

        first = True
        for plot_data, _ in zip(all_plot_data, all_scatter_data):
            x, y = plot_data
            if not first:
                # Добавляем три NaN-точки между сегментами
                plot_segments_x.extend([np.nan, np.nan, np.nan])
                plot_segments_y.extend([np.nan, np.nan, np.nan])
            plot_segments_x.extend(x)
            plot_segments_y.extend(y)
            first = False

        # Преобразуем в numpy массивы
        x_arr = np.array(plot_segments_x)
        y_arr = np.array(plot_segments_y)
        scatter_x = np.array(scatter_x)
        scatter_y = np.array(scatter_y)

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
        legend_proxy.opts.update({
            'size': self._style_config['symbol_size'],
            'pen': pg.mkPen(color=self._style_config['color']),
            'brush': pg.mkBrush(self._style_config['fill_color'])
        })
        return legend_proxy

    def _create_curve(self, plot_data):
        x, y = plot_data
        return pg.PlotCurveItem(
            x=x,
            y=y,
            connect='finite',
            pen=pg.mkPen(
                color=self._style_config['color'],
                width=self._style_config.get('width', 2)
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
            pen=pg.mkPen(color=self._style_config['color'])
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
