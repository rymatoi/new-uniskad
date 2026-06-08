from PySide6 import QtCore
import pyqtgraph as pg
import pyqtgraph.functions as fn
import matplotlib

matplotlib.use('Qt5Agg')
matplotlib.use('module://app.utils.backend_emf')
import matplotlib.pyplot as plt


def _clean_axes(axl):
    if type(axl) is not list:
        axl = [axl]
    for ax in axl:
        if ax is None:
            continue
        for loc, spine in ax.spines.items():
            if loc in ['left', 'bottom']:
                pass
            elif loc in ['right', 'top']:
                spine.set_color('none')
                # do not draw the spine
            else:
                raise ValueError('Unknown spine location: %s' % loc)
            # turn off ticks when there is no spine
            ax.xaxis.set_ticks_position('bottom')


def plot_to_mpl_figure(plot: pg.PlotItem, item) -> plt.Figure:
    plt.tight_layout()
    # fig = plt.figure(figsize=(12, 8))
    fig = plt.figure()
    fig.set_size_inches(12, 8)
    # fig.subplots_adjust(left=1, right=1, top=1, bottom=1)

    # get labels from the graphic item
    x_label = plot.axes['bottom']['item'].label.toPlainText()
    y_label = plot.axes['left']['item'].label.toPlainText()
    title = plot.titleLabel.text

    ax = fig.add_subplot(111, title=title)
    ax.clear()

    # Установка шага сетки
    # x_step = plot.getAxis('bottom').tickValues()[1] - plot.getAxis('bottom').tickValues()[0]
    # y_step = plot.getAxis('left').tickValues()[1] - plot.getAxis('left').tickValues()[0]
    if item.graph_x_major_step:
        ax.xaxis.set_major_locator(plt.MultipleLocator(float(item.graph_x_major_step)))
    if item.graph_y_major_step:
        ax.yaxis.set_major_locator(plt.MultipleLocator(float(item.graph_y_major_step)))

    ax.grid(True)  # Add grid

    for item in plot.curves:
        x, y = item.getData()
        if x is None or y is None:
            continue
        opts = item.opts
        pen = fn.mkPen(opts['pen'])
        if pen.style() == QtCore.Qt.NoPen:
            line_style = ''
        else:
            line_style = '-'
        color = tuple([c / 255. for c in fn.colorTuple(pen.color())])
        symbol = opts['symbol']
        # if symbol == 't':
        #     symbol = '^'
        symbolPen = fn.mkPen(opts['symbolPen'])

        if symbol_color := opts['symbolBrush']:
            symbolBrush = fn.mkBrush(symbol_color)
            markerfacecolor = tuple([c / 255. for c in fn.colorTuple(symbolBrush.color())])
        else:
            markerfacecolor = None

        markeredgecolor = tuple([c / 255. for c in fn.colorTuple(symbolPen.color())])
        markersize = opts['symbolSize']

        if opts['fillLevel'] is not None and opts['fillBrush'] is not None:
            fillBrush = fn.mkBrush(opts['fillBrush'])
            fillcolor = tuple([c / 255. for c in fn.colorTuple(fillBrush.color())])
            ax.fill_between(x=x, y1=y, y2=opts['fillLevel'], facecolor=fillcolor)
        symbol_mapping = {
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
        pl = ax.plot(x, y, marker=symbol_mapping.get(symbol, symbol), color=color, linewidth=pen.width(),
                     linestyle=line_style, markeredgecolor=markeredgecolor,
                     markerfacecolor=markerfacecolor,
                     markersize=markersize)

        xr, yr = plot.viewRange()
        ax.set_xbound(*xr)
        ax.set_ybound(*yr)

    ax.set_xlabel(x_label)  # place the labels.
    ax.set_ylabel(y_label)

    return fig
