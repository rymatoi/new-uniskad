import ast
import re
from PySide2.QtWidgets import QTreeWidgetItem, QDialog, QTreeWidgetItemIterator
from app import basic_funcs
from app.plugins.base_state.dialogs.edit_user_formula import EditUserFormulaDialog
from app.plugins.project import utils
from db import sp
from db.schemas import UserFormula
from db.tables import USER_FORMULA
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_manage_user_formulas import Ui_ListTemplateFormulas


class FormulaTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.need_update = False
        self.scheme = USER_FORMULA
        self.modified_formula = self.render_formula()
        self.name = self._data.prop_value
        self.setText(1, self._data.prop_value)
        self.setText(2, self.modified_formula)
        self.setData(0, 1, self._data)

    def render_formula(self):
        item = self._data
        if not item:
            return ''
        arg_dict = {f'X{i}': arg for i, arg in enumerate(ast.literal_eval(item.x_vals))}

        def replace_variables(match):
            return f'"{arg_dict[match.group(0)]}"'

        pattern = r'\b(' + '|'.join(re.escape(key) for key in arg_dict.keys()) + r')\b'
        return re.sub(pattern, replace_variables, item.param_formula)


class ManageUserFormulasDialog(BaseDialog):
    def __init__(self, parent, main_window=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_ListTemplateFormulas()
        self.ui.setupUi(self)

        self._parent = parent
        self.mw = main_window

        self.ui.treeWidget.setHeaderLabels(['№', 'Имя параметра', 'Формула определения параметра'])
        self.init_tree()

        self.root_items = [self.ui.treeWidget.topLevelItem(i) for i in range(self.ui.treeWidget.topLevelItemCount())]

        self.create_connections()

    def init_tree(self):
        formula_list = sp.get_user_formula_list()
        for formula in formula_list:
            item = FormulaTreeWidgetItem(formula)
            self.ui.treeWidget.addTopLevelItem(item)
        self.update_indices()

    def create_connections(self):
        self.ui.cancelPushButton.clicked.connect(self.cancel)
        self.ui.savePushButton.clicked.connect(self.accept)
        self.ui.addPushButton.clicked.connect(self.add_row)
        self.ui.editPushButton.clicked.connect(self.edit_row)
        self.ui.removePushButton.clicked.connect(self.remove_row)
        self.ui.addParamsPushButton.clicked.connect(self.add_params_to_table)
        self.ui.upButton.clicked.connect(self.move_item_up)
        self.ui.downButton.clicked.connect(self.move_item_down)

    def update_indices(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        index = 0
        while iterator.value():
            item = iterator.value()
            item.setText(0, str(index + 1))
            index += 1
            iterator += 1

    def add_params_to_table(self):
        self.save_new_formulas()
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            self._parent.add_row(None, item.text(1), '=' + item.text(2))

    def remove_row(self):
        selected_items = self.ui.treeWidget.selectedItems()
        if selected_items:
            for item in selected_items:
                index = self.ui.treeWidget.indexOfTopLevelItem(item)
                self.ui.treeWidget.takeTopLevelItem(index)
            self.update_indices()

    def add_row(self):
        param_name = basic_funcs.get_text('Создание формулы', 'Напишите название параметра:', 'Новый параметр')
        new_data = UserFormula({
            'id_record': None,
            'param_formula': '',
            'prop_name': 'name',
            'prop_value': param_name,
            'x_vals': '[]',
            'user_id': None,
            'id': None,
            'id_up': -1
        })
        new_item = FormulaTreeWidgetItem(new_data)
        self.ui.treeWidget.addTopLevelItem(new_item)
        self.update_indices()

    def move_item_up(self):
        index = self.ui.treeWidget.indexOfTopLevelItem(self.ui.treeWidget.currentItem())
        if index > 0:
            item = self.ui.treeWidget.takeTopLevelItem(index)
            self.ui.treeWidget.insertTopLevelItem(index - 1, item)
            self.update_indices()

    def move_item_down(self):
        index = self.ui.treeWidget.indexOfTopLevelItem(self.ui.treeWidget.currentItem())
        if index < self.ui.treeWidget.topLevelItemCount() - 1:
            item = self.ui.treeWidget.takeTopLevelItem(index)
            self.ui.treeWidget.insertTopLevelItem(index + 1, item)
            self.update_indices()

    def edit_row(self):
        selected_items = self.ui.treeWidget.selectedItems()
        if selected_items:
            item = selected_items[0]
            dialog = EditUserFormulaDialog(item, self, self.mw)
            if dialog.exec_():  # Если произошло изменение данных
                arg_list, formula, name = dialog.get_result()
                self.render_formula(arg_list, formula, item)
                item.need_update = True
                item.setText(1, name)
                item._data.prop_value = name

    def render_formula(self, arg_list, formula, item):
        item._data.param_formula = formula
        item._data.x_vals = str(arg_list)
        item.modified_formula = item.render_formula()
        item.setText(2, item.modified_formula)

    def save_new_formulas(self):
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            if item.need_update:
                formula = sp.new_user_formula(item._data.table_fit(item.scheme))
                item.need_update = False
            if item in self.root_items:
                self.root_items.remove(item)
        for item in self.root_items:
            sp.remove_user_formula(item._data.table_fit(item.scheme))

        self.root_items.clear()
        self.root_items = [self.ui.treeWidget.topLevelItem(i) for i in range(self.ui.treeWidget.topLevelItemCount())]

    def accept(self):
        self.save_new_formulas()
        super().accept()

    def cancel(self):
        self.close()

    @classmethod
    def modal(cls, parent=None):
        wnd = cls(parent)
        return wnd.exec_()
