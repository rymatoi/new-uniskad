from PySide6.QtWidgets import QTreeWidgetItem, QDialog, QTreeWidgetItemIterator, QTreeWidget, QAbstractItemView
from app import basic_funcs
from app.plugins.base_state.dialogs.test_data_selection import TestDataSelectionDialog
from app.plugins.project import utils
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_formula import Ui_EditFormulaDialog


class RowParam:
    def __init__(self, data):
        self.id = data
        self.prop_value = data
        self.base_name = data


class EditUserFormulaDialog(BaseDialog):
    def __init__(self, item, parent, main_window=None, flags=None, *args, **kwargs):
        super().__init__(parent, flags)
        self.ui = Ui_EditFormulaDialog()
        self.ui.setupUi(self)

        self._parent = parent
        self.mw = main_window
        self.item = item

        self.ui.formulaLineEdit.setText(self.item._data.param_formula)
        self.ui.lineEdit.setText(self.item.name)

        self.arg_list = basic_funcs.str_to_list(self.item._data.x_vals)
        self.x_count = len(self.arg_list)

        self.ui.treeWidget.setHeaderLabels(['Имя переменной', 'Параметр'])
        self.init_tree(self.arg_list)

        self.create_connections()

    def init_tree(self, params):
        for param in params:
            item = QTreeWidgetItem(self.ui.treeWidget)
            item.setText(0, f'X{self.ui.treeWidget.indexOfTopLevelItem(item)}')
            item.setText(1, param)
            item.setData(0, 1, param)

    def create_connections(self):
        self.ui.cancelPushButton.clicked.connect(self.cancel)
        self.ui.savePushButton.clicked.connect(self.accept)
        self.ui.addPushButton.clicked.connect(self.add_row)
        self.ui.removePushButton.clicked.connect(self.remove_row)
        self.ui.editPushButton.clicked.connect(self.edit_row)

    def add_row(self):
        parameters = utils.collect_project_params(
            sp.get_project_test_params(self._parent._parent.item._parent._data.id))
        dialog = TestDataSelectionDialog(list(parameters.keys()), self.mw)
        if dialog.exec_():
            for param in dialog.res:
                self.x_count += 1
                new_param = param.data()
                self.arg_list.append(new_param)
                item = QTreeWidgetItem(self.ui.treeWidget)
                item.setText(0, f'X{self.ui.treeWidget.indexOfTopLevelItem(item)}')
                item.setText(1, new_param)
                item.setData(0, 1, new_param)
        self.ui.treeWidget.resizeColumnToContents(0)
        self.ui.treeWidget.resizeColumnToContents(1)

    def edit_row(self):
        selected_items = self.ui.treeWidget.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            parameters = utils.collect_project_params(
                sp.get_project_test_params(self._parent._parent.item._parent._data.id))
            dialog = TestDataSelectionDialog(list(parameters.keys()), self.mw)
            dialog.ui.treeView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            dialog.model.CHECKABLE = False
            if dialog.exec_():
                param = dialog.res
                param_name = param.data()
                self.arg_list[self.ui.treeWidget.indexOfTopLevelItem(item)] = param_name
                item.setData(0, 1, param_name)
                item.setText(1, param_name)
                # for param in dialog.res:
                #     self.x_count += 1
                #     new_param = param.data()
                #     self.arg_list.append(new_param)
                #     item = QTreeWidgetItem(self.ui.treeWidget)
                #     item.setText(0, f'X{self.ui.treeWidget.indexOfTopLevelItem(item)}')
                #     item.setText(1, new_param)
                #     item.setData(0, 1, new_param)
            self.ui.treeWidget.resizeColumnToContents(0)
            self.ui.treeWidget.resizeColumnToContents(1)

    def remove_row(self):
        selected_items = self.ui.treeWidget.selectedItems()
        if selected_items:
            for item in selected_items:
                self.arg_list.remove(item.data(0, 1))
                index = self.ui.treeWidget.indexOfTopLevelItem(item)
                self.ui.treeWidget.takeTopLevelItem(index)
            self.update_indices()

    def update_indices(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        index = 0
        while iterator.value():
            item = iterator.value()
            item.setText(0, f'X{index}')
            index += 1
            iterator += 1

    def accept(self):
        self.res = self.arg_list, self.ui.formulaLineEdit.text(), self.ui.lineEdit.text()
        super().accept()

    def cancel(self):
        self.close()

    @classmethod
    def modal(cls, parent=None):
        wnd = cls(parent)
        return wnd.exec_()
