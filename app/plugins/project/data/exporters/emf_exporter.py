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
            print(f"Processing curve: {curve.name()}")

            # Получаем данные
            x = curve.xData
            y = curve.yData

            print(f"Data points: x={len(x)}, y={len(y)}")
            print(f"X range: {min(x)} to {max(x)}")
            print(f"Y range: {min(y)} to {max(y)}")

            if x is None or y is None or len(x) == 0 or len(y) == 0:
                print("Skipping curve - no data")
                continue

            opts = curve.opts
            pen = fn.mkPen(opts['pen'])
            line_style = '' if pen.style() == Qt.NoPen else '-'
            color = tuple([c / 255. for c in fn.colorTuple(pen.color())])

            print(f"Line style: {line_style}")
            print(f"Color: {color}")

            symbol = opts['symbol']
            symbol_pen = fn.mkPen(opts['symbolPen'])

            # Определяем цвет заливки маркера
            if symbol_color := opts['symbolBrush']:
                symbol_brush = fn.mkBrush(symbol_color)
                marker_face_color = tuple([c / 255. for c in fn.colorTuple(symbol_brush.color())])
            else:
                marker_face_color = None

            marker_edge_color = tuple([c / 255. for c in fn.colorTuple(symbol_pen.color())])
            marker_size = opts['symbolSize']

            print(f"Symbol: {symbol}")
            print(f"Marker size: {marker_size}")
            print(f"Marker face color: {marker_face_color}")
            print(f"Marker edge color: {marker_edge_color}")

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
                    linewidth=pen.width(),
                    linestyle=line_style,
                    markeredgecolor=marker_edge_color,
                    markerfacecolor=marker_face_color,
                    markersize=marker_size,
                    label=curve.name(),
                    zorder=2)  # Более высокий zorder для основных точек

        # Устанавливаем пределы осей
        xr, yr = plot_view.plotItem.viewRange()
        print(f"View range: x={xr}, y={yr}")
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
