# -- coding: cp1251--
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMdiArea, QTreeView, QTabWidget, QSplitter, QDockWidget, QWidget, QMainWindow, QVBoxLayout


class Ui_MainWindow(object):
    QSS = """
    QMdiSubWindow:title{
        background: lightgray;
    }
    """

    def setupUi(self, MainWindow):
        self.centralWidget = QMainWindow()
        MainWindow.setCentralWidget(self.centralWidget)
