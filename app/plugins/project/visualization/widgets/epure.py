import numpy as np
from PySide2.QtCore import Qt

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.colors import safe_color
from app.plugins.project.visualization.widgets.legend_proxy import LegendProxyPlotDataItem
import pyqtgraph as pg


class EpureItem(pg.ItemGroup):
    def __init__(self, all_scatter_data, all_plot_data, **kwargs):
        super().__init__()

        self._style_config = self._normalize_style(kwargs.get('style'))
        self._name = self._style_config.get('name', 'Epure')

        # Прокси-элемент для легенды (невидимый на графике)
        self.legend_proxy = self.init_legend_proxy()

        scatter_x, scatter_y = self._combine_scatter_points(all_scatter_data)
        curve_x, curve_y = self._combine_curve_segments(all_plot_data)

        # Создаем scatter и curve элементы
        self.scatter = self._create_scatter((scatter_x, scatter_y))
        self.curve = self._create_curve((curve_x, curve_y))

        # Добавляем элементы в обратном порядке, чтобы точки были поверх линий
        self.addItem(self.curve)
        self.addItem(self.scatter)

        self._update_curve_pen()
        self._update_legend_proxy_style()

        # Синхронизация видимости
        self.legend_proxy.visibilityChanged.connect(self._on_proxy_visibility_changed)

    @property
    def style_config(self):
        return self._style_config

    @staticmethod
    def _ensure_opaque_color(color_value):
        return safe_color(
            color_value,
            GraphConstants.DEFAULT_STYLE['color'],
            force_opaque=True,
        )

    def _normalize_style(self, style):
        base = GraphConstants.DEFAULT_STYLE.copy()
        if style:
            base.update(style)

        def _int_value(value, default):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        normalized = {
            'color': self._ensure_opaque_color(base.get('color')),
            'width': _int_value(base.get('width', GraphConstants.DEFAULT_STYLE['width']),
                               GraphConstants.DEFAULT_STYLE['width']),
            'symbol': base.get('symbol', GraphConstants.DEFAULT_STYLE['symbol']) or GraphConstants.DEFAULT_STYLE['symbol'],
            'symbol_size': _int_value(base.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size']),
                                      GraphConstants.DEFAULT_STYLE['symbol_size']),
            'symbol_color': self._ensure_opaque_color(base.get('symbol_color', base.get('color'))),
            'fill_color': self._ensure_opaque_color(base.get('fill_color', base.get('color'))),
            'name': base.get('name', 'Epure')
        }

        # Тип линии всегда сплошной и непрозрачный для читаемости
        normalized['line_style'] = Qt.SolidLine

        return normalized

    def init_legend_proxy(self):
        legend_proxy = LegendProxyPlotDataItem([], [], name=self._name, style=self._style_config)
        legend_proxy.setVisible(True)
        legend_proxy.opts.update({
            'size': self._style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size']),
            'pen': pg.mkPen(color=self._style_config['color'], style=Qt.SolidLine,
                            width=self._style_config.get('width', GraphConstants.DEFAULT_STYLE['width'])),
            'brush': pg.mkBrush(self._style_config['fill_color']),
            'symbolPen': pg.mkPen(self._style_config.get('symbol_color', self._style_config['color']))
        })
        return legend_proxy

    def _create_curve(self, plot_data):
        x, y = plot_data
        curve = pg.PlotCurveItem(
            x=x,
            y=y,
            connect='finite',
            pen=pg.mkPen(
                color=self._style_config['color'],
                width=self._style_config.get('width', 2),
                style=Qt.SolidLine
            )
        )
        curve.setShadowPen(None)
        return curve

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

    def _combine_scatter_points(self, scatter_sequences):
        if not scatter_sequences:
            return np.empty(0, dtype=float), np.empty(0, dtype=float)

        xs = []
        ys = []
        for x_values, y_values in scatter_sequences:
            x_arr = np.asarray(x_values, dtype=float)
            y_arr = np.asarray(y_values, dtype=float)
            if x_arr.size == 0 or y_arr.size == 0:
                continue
            xs.append(x_arr)
            ys.append(y_arr)

        if not xs:
            return np.empty(0, dtype=float), np.empty(0, dtype=float)

        return np.concatenate(xs), np.concatenate(ys)

    def _combine_curve_segments(self, curve_sequences):
        if not curve_sequences:
            return np.empty(0, dtype=float), np.empty(0, dtype=float)

        segments_x = []
        segments_y = []
        for index, (x_values, y_values) in enumerate(curve_sequences):
            x_arr = np.asarray(x_values, dtype=float)
            y_arr = np.asarray(y_values, dtype=float)
            if x_arr.size == 0 or y_arr.size == 0:
                continue

            if segments_x:
                gap = np.full(3, np.nan, dtype=float)
                segments_x.append(gap)
                segments_y.append(gap)

            segments_x.append(x_arr)
            segments_y.append(y_arr)

        if not segments_x:
            return np.empty(0, dtype=float), np.empty(0, dtype=float)

        return np.concatenate(segments_x), np.concatenate(segments_y)

    def _update_curve_pen(self):
        pen = pg.mkPen(
            color=self._style_config['color'],
            width=self._style_config.get('width', GraphConstants.DEFAULT_STYLE['width']),
            style=Qt.SolidLine
        )
        self.curve.setPen(pen)

    def _update_legend_proxy_style(self):
        self.legend_proxy._style_config.update(self._style_config)
        self.legend_proxy.apply_style()
        self.legend_proxy.opts.update({
            'size': self._style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size']),
            'pen': pg.mkPen(color=self._style_config['color'], style=Qt.SolidLine,
                            width=self._style_config.get('width', GraphConstants.DEFAULT_STYLE['width'])),
            'brush': pg.mkBrush(self._style_config['fill_color']),
            'symbolPen': pg.mkPen(self._style_config.get('symbol_color', self._style_config['color']))
        })
        self.legend_proxy.opts['name'] = self._name

    def update_data(self, all_scatter_data, all_plot_data, style=None):
        if style:
            self._style_config = self._normalize_style(style)
            self._name = self._style_config.get('name', self._name)

        scatter_x, scatter_y = self._combine_scatter_points(all_scatter_data)
        curve_x, curve_y = self._combine_curve_segments(all_plot_data)

        self.scatter.setData(
            x=scatter_x,
            y=scatter_y,
            symbol=self._style_config['symbol'],
            size=self._style_config.get('symbol_size', GraphConstants.DEFAULT_STYLE['symbol_size']),
            brush=pg.mkBrush(self._style_config['fill_color']),
            pen=pg.mkPen(self._style_config.get('symbol_color', self._style_config['color']))
        )
        self.curve.setData(x=curve_x, y=curve_y, connect='finite')
        self._update_curve_pen()
        self._update_legend_proxy_style()

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
        """EpureItem does not behave like a standard PlotDataItem for legends.

        We provide a dedicated legend proxy, so we prevent PyQtGraph from
        auto-registering this item as ``plotData`` to avoid duplicate legend
        entries.
        """
        if interface is None:
            return []
        return False

    def _on_proxy_visibility_changed(self, visible: bool):
        self._apply_visibility(visible, update_proxy=False)

    def _apply_visibility(self, visible: bool, update_proxy: bool = True):
        """Применяет изменение видимости ко всем связанным элементам."""
        super().setVisible(visible)

        if self.curve:
            self.curve.setVisible(visible)
        if self.scatter:
            self.scatter.setVisible(visible)

        if update_proxy and self.legend_proxy.isVisible() != visible:
            self.legend_proxy.setVisible(visible)

    def setVisible(self, visible: bool):  # noqa: N802 - соответствие Qt API
        """Обеспечивает синхронизацию видимости с легендой."""
        self._apply_visibility(visible, update_proxy=True)

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
