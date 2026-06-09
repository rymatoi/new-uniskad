# -- coding: cp1251--
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMdiArea, QTreeView, QTabWidget, QSplitter, QDockWidget, QWidget, QMainWindow, QVBoxLayout


class Ui_MainWindow(object):
    QSS = """
    QMdiSubWindow:title{
        background: lightgray;
    }
    """

    def setupUi(self, MainWindow):
        self.centralWidget = QMainWindow()
        MainWindow.setCentralWidget(self.centralWidget)
