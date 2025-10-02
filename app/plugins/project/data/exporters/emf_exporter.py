import matplotlib

matplotlib.use('module://app.utils.backend_emf')
import matplotlib.pyplot as plt
import pyqtgraph.functions as fn
from PySide2.QtCore import Qt
import numpy as np


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
            Qt.NoPen: 'none',
            Qt.SolidLine: '-',
            Qt.DashLine: '--',
            Qt.DotLine: ':',
            Qt.DashDotLine: '-.',
            Qt.DashDotDotLine: (0, (3, 5, 1, 5, 1, 5)),
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

        # Настройка сетки
        if hasattr(plot_view, 'graph_x_major_step') and plot_view.graph_x_major_step:
            ax.xaxis.set_major_locator(plt.MultipleLocator(float(plot_view.graph_x_major_step)))
        if hasattr(plot_view, 'graph_y_major_step') and plot_view.graph_y_major_step:
            ax.yaxis.set_major_locator(plt.MultipleLocator(float(plot_view.graph_y_major_step)))

        ax.grid(True)

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
