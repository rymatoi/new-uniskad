from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeWidgetItem

from app.plugins.base_state.widgets import ExtendedComboBox
from app.plugins.project import utils
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_extra_param_epure import Ui_ExtraParamEoure


class ExtraParamEpureDialog(BaseDialog):

    def __init__(self, test_nodes, project_id, extra_param, extra_param_values, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.project_id = project_id
        self.test_nodes = test_nodes
        self.ui = Ui_ExtraParamEoure()
        self.ui.setupUi(self)
        self.comboBox = ExtendedComboBox(self)
        self.ui.verticalLayout.replaceWidget(self.ui.comboBox, self.comboBox)
        self.ui.comboBox.deleteLater()
        self.ui.comboBox.hide()
        self.ui.comboBox = None

        self.selected = extra_param_values

        self.param_list = utils.collect_project_params(sp.get_project_test_params(project_id))
        self.param_values_dict = {}
        self.current_param = extra_param
        self.create_connections()  # создаем привязки

        self.ui.treeWidget.setHeaderLabel('')

        self.load_params()

    def create_connections(self):
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.close)
        self.comboBox.currentTextChanged.connect(self.load_param_values)

    def load_params(self):
        self.comboBox.addItems(['Пусто'] + list(self.param_list.keys()))
        self.comboBox.setCurrentText(self.current_param if self.current_param else 'Пусто')

    def load_param_values(self, text):
        if text == 'Пусто':
            self.fill_tree_widget([])
            self.current_param = None
            return

        if text not in self.param_list:
            return

        self.current_param = text

        if text not in self.param_values_dict:
            z_data = utils.collect_cell_values(
                sp.get_x_curves(self.project_id, [test._data.project_id for test in self.test_nodes],
                                text))
            self.param_values_dict[text] = []
            for val in list(z_data.values()):
                self.param_values_dict[text] += val

        self.fill_tree_widget(set(self.param_values_dict[text]))

    def fill_tree_widget(self, values):
        self.ui.treeWidget.clear()
        for val in values:
            child = QTreeWidgetItem(self.ui.treeWidget)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setCheckState(0, Qt.Unchecked if val.prop_value not in self.selected else Qt.Checked)
            child.setText(0, val.prop_value)

    def accept(self) -> None:
        res = []
        root = self.ui.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) is Qt.CheckState.Checked:
                res.append(item.text(0))
        self.res = self.current_param, res
        super().accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
