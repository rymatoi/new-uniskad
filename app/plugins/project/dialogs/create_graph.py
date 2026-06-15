import json

from PySide2.QtCore import QItemSelection
from PySide2.QtWidgets import QDialogButtonBox, QComboBox

from app.plugins.base_state.widgets import ExtendedComboBox
from app.plugins.project import utils
from app.plugins.project.utils_ import get_param_values, get_project_params
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_create_graph import Ui_CreateGraphDialog


class CreateGraphDialog(BaseDialog):

    def __init__(self, project_id, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_CreateGraphDialog()
        self.ui.setupUi(self)

        self.curves = {}
        self.param_values = {}
        self.project_id = project_id
        self.XComboBox = ExtendedComboBox(self)
        self.YComboBox = ExtendedComboBox(self)
        self.ZComboBox = ExtendedComboBox(self)

        self.ui.toDoubleSpinBox.setMaximum(1000000)
        self.ui.fromDoubleSpinBox.setMaximum(1000000)

        self.ui.toDoubleSpinBox.setMinimum(-1000000)
        self.ui.fromDoubleSpinBox.setMinimum(-1000000)

        self.init_widgets()
        self.init_values(project_id)

        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.create_graph)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.XComboBox.currentTextChanged.connect(self.update_name)
        self.YComboBox.currentTextChanged.connect(self.update_name)
        self.ZComboBox.currentTextChanged.connect(self.update_values)
        self.ui.acceptPushButton.clicked.connect(self.add_param)
        self.ui.deletePushButton.clicked.connect(self.delete_param)
        self.ui.listWidget.clicked.connect(self.change_selected_param)

        self.ui.toDoubleSpinBox.valueChanged.connect(self.save_to_value)
        self.ui.fromDoubleSpinBox.valueChanged.connect(self.save_from_value)

    def change_selected_param(self, index):
        if index.isValid():
            self.ZComboBox.setCurrentText(self.ui.listWidget.item(index.row()).text())

    def valid_param(self):
        if self.ZComboBox.currentText() not in self.param_values.keys():
            return False
        return True

    def save_from_value(self):
        if self.valid_param():
            self.param_values[self.ZComboBox.currentText()].min_val = self.ui.fromDoubleSpinBox.value()

    def save_to_value(self):
        if self.valid_param():
            self.param_values[self.ZComboBox.currentText()].max_val = self.ui.toDoubleSpinBox.value()

    def add_param(self):
        if self.valid_param():
            self.ui.listWidget.addItem(self.ZComboBox.currentText())

    def delete_param(self):
        if len(self.ui.listWidget.selectedIndexes()) == 0:
            return
        for index in self.ui.listWidget.selectedIndexes():
            self.ui.listWidget.takeItem(index.row())

    def init_widgets(self):
        self.ui.formLayout_2.replaceWidget(self.ui.XComboBox, self.XComboBox)
        self.ui.XComboBox.deleteLater()
        self.ui.XComboBox.hide()
        self.ui.XComboBox = None

        self.ui.formLayout_2.replaceWidget(self.ui.YComboBox, self.YComboBox)
        self.ui.YComboBox.deleteLater()
        self.ui.YComboBox.hide()
        self.ui.YComboBox = None

        self.ui.formLayout_5.replaceWidget(self.ui.comboBox, self.ZComboBox)
        self.ui.comboBox.deleteLater()
        self.ui.comboBox.hide()
        self.ui.comboBox = None

    def update_name(self):
        self.ui.nameLineEdit.setText(f'{self.YComboBox.currentText()} от {self.XComboBox.currentText()}')

    def update_values(self):
        self._ensure_param_values(self.ZComboBox.currentText())
        if not self.valid_param():
            return
        cur_param = self.param_values[self.ZComboBox.currentText()]
        if cur_param.min_val is None:
            cur_param.min_val = 0
        if cur_param.max_val is None:
            cur_param.max_val = 0
        self.ui.fromDoubleSpinBox.setValue(cur_param.min_val)
        self.ui.toDoubleSpinBox.setValue(cur_param.max_val)

    def init_values(self, project_id):
        class Values:
            def __init__(self, max_val, min_val):
                self.max_val = max_val
                self.min_val = min_val

        self.curves = get_project_params(project_id)
        curve_list = list(self.curves.keys())
        self.ZComboBox.addItems(curve_list)
        self.XComboBox.addItems(curve_list)
        self.YComboBox.addItems(curve_list)
        self.XComboBox.setCurrentText('')
        self.YComboBox.setCurrentText('')
        self.update_name()

    def _ensure_param_values(self, param_name):
        if not param_name or param_name in self.param_values:
            return
        _curves = get_param_values(self.project_id, param_name)
        for _c in _curves:
            if _c.param not in self.param_values.keys():
                self.param_values[_c.param] = Values(_c.value, _c.value)
            if _c.value is None or self.param_values[_c.param].max_val is None or self.param_values[
                _c.param].min_val is None:
                continue
            if _c.value > self.param_values[_c.param].max_val:
                self.param_values[_c.param].max_val = _c.value
            if _c.value < self.param_values[_c.param].min_val:
                self.param_values[_c.param].min_val = _c.value

    def get_group_by(self):
        if self.ui.modelRadioButton.isChecked():
            group_by = 'model'
        elif self.ui.assemblyRadioButton.isChecked():
            group_by = 'assembly'
        elif self.ui.productRadioButton.isChecked():
            group_by = 'product'
        else:
            group_by = ''
        return group_by

    def get_constraints(self):
        c = {}
        for i in range(self.ui.listWidget.count()):
            param = self.ui.listWidget.item(i).text()
            c[param] = {
                'min': self.param_values[param].min_val,
                'max': self.param_values[param].max_val,
            }
        return json.dumps(c)

    def create_graph(self):
        group_by = self.get_group_by()
        constraints = self.get_constraints()
        result = {
            'x_curve': self.XComboBox.currentText(),
            'y_curve': self.YComboBox.currentText(),
            'graph_name': self.ui.nameLineEdit.text(),
            'group_by': group_by,
            'constraints': constraints
        }
        self.res = result
        self.accept()

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
