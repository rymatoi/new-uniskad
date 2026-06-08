import math

import matplotlib

matplotlib.use('module://app.utils.backend_emf')
import matplotlib.pyplot as plt
import pyqtgraph.functions as fn
from matplotlib.ticker import MultipleLocator
from PySide6.QtCore import Qt


class PlotEMFExporter:
    """Класс для экспорта данных графика в EMF с сохранением стилей."""

    def __init__(self):
        self.symbol_mapping = {
            'o': 'o',  # Круг
            't': 'v',  # Треугольник вниз
            't1': '^',  # Треугольник вверх
            't2': '>',  # Треугольник вправо
            't3': '<',  # Треугольник влево
            's': 's',  # Квадрат
            'p': 'p',  # Пятиугольник
            'h': 'H',  # Восьмиугольник
            'star': '*',  # Звезда
            '+': '+',  # Плюс
            'd': 'D',  # Призма
            'x': 'X',  # Крест
        }
        self.line_style_map = {
            Qt.PenStyle.NoPen: 'none',
            Qt.PenStyle.SolidLine: '-',
            Qt.PenStyle.DashLine: '--',
            Qt.PenStyle.DotLine: ':',
            Qt.PenStyle.DashDotLine: '-.',
            Qt.PenStyle.DashDotDotLine: (0, (3, 5, 1, 5, 1, 5)),
        }

    def _clean_axes(self, ax):
        """Очищает лишние элементы осей."""
        for loc, spine in ax.spines.items():
            if loc in ['left', 'bottom']:
                pass
            elif loc in ['right', 'top']:
                spine.set_color('none')
            else:
                raise ValueError('Unknown spine location: %s' % loc)
        ax.xaxis.set_ticks_position('bottom')

    def export(self, plot_view, filename):
        """Экспортирует график в EMF файл."""
        plt.tight_layout()
        fig = plt.figure()
        fig.set_size_inches(12, 8)

        # Получаем подписи осей
        x_label = plot_view.plotItem.axes['bottom']['item'].label.toPlainText()
        y_label = plot_view.plotItem.axes['left']['item'].label.toPlainText()
        title = plot_view.plotItem.titleLabel.text

        ax = fig.add_subplot(111, title=title)
        ax.clear()

        if hasattr(plot_view, 'get_effective_grid_settings'):
            grid_settings = plot_view.get_effective_grid_settings()
        elif hasattr(plot_view, 'get_grid_settings'):
            grid_settings = plot_view.get_grid_settings()
        else:
            grid_settings = {}
        x_grid = grid_settings.get('x', {'auto': True})
        y_grid = grid_settings.get('y', {'auto': True})

        def _sanitize(value):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                return None

            if math.isclose(numeric, 0.0, abs_tol=1e-12):
                return None

            return abs(numeric)

        x_major = _sanitize(x_grid.get('major')) if x_grid else None
        y_major = _sanitize(y_grid.get('major')) if y_grid else None
        x_minor = _sanitize(x_grid.get('minor')) if x_grid else None
        y_minor = _sanitize(y_grid.get('minor')) if y_grid else None

        if x_major is not None:
            ax.xaxis.set_major_locator(MultipleLocator(x_major))
        if y_major is not None:
            ax.yaxis.set_major_locator(MultipleLocator(y_major))

        if x_minor is None and x_major is not None:
            x_minor = x_major / 5
        if y_minor is None and y_major is not None:
            y_minor = y_major / 5

        minor_enabled = False
        if x_minor is not None:
            ax.xaxis.set_minor_locator(MultipleLocator(x_minor))
            minor_enabled = True
        if y_minor is not None:
            ax.yaxis.set_minor_locator(MultipleLocator(y_minor))
            minor_enabled = True

        ax.grid(True, which='major')
        if minor_enabled:
            ax.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.6)
        else:
            ax.grid(False, which='minor')

        # Отрисовываем каждую кривую
        for curve in plot_view.plotItem.curves:

            # Получаем данные
            x = curve.xData
            y = curve.yData

            if x is None or y is None or len(x) == 0 or len(y) == 0:
                continue

            opts = curve.opts
            pen = fn.mkPen(opts['pen'])
            qt_pen_style = pen.style()
            line_style = self.line_style_map.get(qt_pen_style, '-')
            line_width = pen.width()
            if line_style == 'none':
                line_width = 0
            color = tuple([c / 255. for c in fn.colorTuple(pen.color())])

            symbol = opts['symbol']
            symbol_pen = fn.mkPen(opts['symbolPen'])

            # Определяем цвет заливки маркера
            if symbol_color := opts['symbolBrush']:
                symbol_brush = fn.mkBrush(symbol_color)
                marker_face_color = tuple([c / 255. for c in fn.colorTuple(symbol_brush.color())])
            else:
                marker_face_color = 'none'

            marker_edge_color = tuple([c / 255. for c in fn.colorTuple(symbol_pen.color())])
            marker_size = opts['symbolSize']

            # Сначала отрисовываем выделенные точки
            if curve in plot_view.selected_points and plot_view.selected_points[curve]:
                selected_indices = list(plot_view.selected_points[curve])
                if selected_indices:  # Если есть выделенные точки
                    selected_x = x[selected_indices]
                    selected_y = y[selected_indices]
                    
                    # Используем тот же размер что и у обычных точек, но немного больше
                    base_size = opts['symbolSize']
                    selected_size = base_size * 1.5
                    
                    # Отрисовываем выделенные точки с низким zorder
                    ax.scatter(selected_x, selected_y,
                             marker=self.symbol_mapping.get(symbol, symbol),
                             s=selected_size**2,
                             color='red',
                             zorder=1)  # Самый низкий zorder

            # Затем отрисовываем линию и основные точки
            ax.plot(x, y,
                    marker=self.symbol_mapping.get(symbol, symbol),
                    color=color,
                    linewidth=line_width,
                    linestyle=line_style,
                    markeredgecolor=marker_edge_color,
                    markerfacecolor=marker_face_color,
                    markersize=marker_size,
                    label=curve.name(),
                    zorder=2)  # Более высокий zorder для основных точек

        # Устанавливаем пределы осей
        xr, yr = plot_view.plotItem.viewRange()
        ax.set_xbound(*xr)
        ax.set_ybound(*yr)

        # Добавляем легенду
        if any(curve.name() for curve in plot_view.plotItem.curves):
            ax.legend()

        # Устанавливаем подписи осей
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        # Очищаем лишние элементы осей
        self._clean_axes(ax)

        # Добавляем отступы
        plt.tight_layout()

        # Сохраняем в EMF
        plt.savefig(filename)
        plt.close(fig)
