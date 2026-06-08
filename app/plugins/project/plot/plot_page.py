from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg
from PySide6.QtWidgets import QStatusBar, QLabel, QFrame

from app.plugins.project.visualization.views.plot_views.epure_view import EpureView
from app.plugins.project.visualization.views.plot_views.plot_view import PlotView


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFrameShape(QFrame.Shape.VLine)


class PlotPage(QtWidgets.QWidget):
    """
    Виджет для отображения графика.
    """

    def __init__(self, item, parent, main_window=None):
        """

        :param item: объект GraphNode
        :param parent:
        """
        super().__init__(parent)
        self.main_window = main_window
        pg.setConfigOptions(background='w', foreground='k', antialias=True)
        self.item = item

        self.centralLayout = QtWidgets.QVBoxLayout()

        self.toolbar = QtWidgets.QToolBar(parent)
        self.plotView = PlotView(item=item, main_window=self.main_window,
                                 parent=self) if item.internal_type() == 'graph' else EpureView(item=item,
                                                                                                main_window=self.main_window,
                                                                                                parent=self)
        self.plotView.set_main_window(self.main_window)

        self.statusbar = QStatusBar(self)
        self.x_label = QLabel()
        self.y_label = QLabel()

        self.statusbar.addPermanentWidget(self.x_label)
        self.statusbar.addPermanentWidget(VLine())
        self.statusbar.addPermanentWidget(self.y_label)

        self.centralLayout.addWidget(self.plotView)
        self.centralLayout.addWidget(self.statusbar)
        self.setLayout(self.centralLayout)

        self.plotView.prepare_curves()
        self._init_toolbar()

        self.update_status_bar()

        self.plotView.sigRangeChanged.connect(lambda: self.update_status_bar())

    def closeEvent(self, event) -> None:
        # self.plotView.commit_changes() #todo надо сохранять изменения
        self.close()

    def update_status_bar(self):
        view_rect = self.plotView.viewRect()
        x_range = f'X : [{round(view_rect.left(), 2)}, {round(view_rect.right(), 2)}]'
        y_range = f'Y : [{round(view_rect.bottom(), 2)}, {round(view_rect.top(), 2)}]'
        self.x_label.setText(x_range)
        self.y_label.setText(y_range)

    def _init_toolbar(self):
        self.toolbar.setIconSize(QtCore.QSize(18, 18))
        self.centralLayout.setMenuBar(self.toolbar)

    def add_toolbar_action(self, action_name, action, toggled=None):
        # if action_name in self.plotView.available_actions: # todo надо проверять доступно ли действие
        setattr(self, action_name, action)
        self.toolbar.addAction(getattr(self, action_name))
        if toggled is not None:
            getattr(self, action_name).toggled.connect(toggled)
            getattr(self, action_name).setCheckable(True)

    def refresh(self, index=None):
        self.plotView.refresh()
