from PySide2.QtWidgets import QDialogButtonBox, QTableWidgetItem

from app import basic_funcs
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_oy_setup import Ui_OYSetupDialog


class OYSetupDialog(BaseDialog):

    def __init__(self, param_list, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_OYSetupDialog()
        self.ui.setupUi(self)
        self.param_list = param_list
        self.init_table()
        self.create_connections()  # создаем привязки

    def create_connections(self):
        self.ui.acceptButton.clicked.connect(self.accept_)
        self.ui.cancelButton.clicked.connect(self.close)

    def init_table(self):
        self.ui.tableWidget.setRowCount(len(self.param_list))
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(["Параметр", "Значение OY"])

        for i, param in enumerate(self.param_list):
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(param))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(str(i)))

        self.ui.tableWidget.resizeColumnsToContents()

    def accept_(self) -> None:
        self.res = []
        for i in range(len(self.param_list)):
            val = self.ui.tableWidget.item(i, 1).text()
            if not val.isdecimal() or not val.isdigit():
                basic_funcs.info('Неверные значения OY',
                                 f'Значения по оси OY должны быть числами. {val} не является числом')
                return
            self.res.append(float(self.ui.tableWidget.item(i, 1).text()))
        super().accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
