import json

from app import app_logger, basic_funcs
from app.basic_funcs import to_float, to_bool
from app.plugins.base_state.widgets import ExtendedComboBox
from app.plugins.project import utils, utils_
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_plane import Ui_EditPlaneDialog

logger = app_logger.get_logger(__name__)

class Values:
    def __init__(self, max_val, min_val):
        self.max_val = max_val
        self.min_val = min_val

class EditPlaneDialog(BaseDialog):
    """Диалог редактирования свойств графика"""

    def __init__(self, plotview, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.plotview = plotview

        self.x_label = plotview.graph_label_x
        self.y_label = plotview.graph_label_y
        self.curves = None
        self.param_values = {}
        self.project_id = None

        self.XComboBox = ExtendedComboBox(self)
        self.YComboBox = ExtendedComboBox(self)
        self.ZComboBox = ExtendedComboBox(self)
        self.axis_params_changed = False

        # Инициализация ui объекта
        self.ui = Ui_EditPlaneDialog()
        self.ui.setupUi(self)
        self.init_widgets()

        project_item = plotview.parent().parent()
        # Осуществляем привязку

        self.create_connections()
        self.init_values(project_item._data.project_id)
        self.refresh()

    def create_connections(self):
        """Функция привязки слотов"""
        self.ui.okButton.clicked.connect(self.apply)
        self.ui.cancelButton.clicked.connect(self.close)

        self.ui.xGridManually.clicked.connect(lambda: self.x_grid_man_clicked())
        self.ui.yGridManually.clicked.connect(lambda: self.y_grid_man_clicked())
        self.ui.xGridAuto.clicked.connect(lambda: self.x_grid_auto_clicked())
        self.ui.yGridAuto.clicked.connect(lambda: self.y_grid_auto_clicked())

        self.ui.xMajor.textChanged.connect(lambda: self.manually_checked())
        self.ui.xMinor.textChanged.connect(lambda: self.manually_checked())
        self.ui.yMajor.textChanged.connect(lambda: self.manually_checked())
        self.ui.yMinor.textChanged.connect(lambda: self.manually_checked())

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

    def init_widgets(self):
        self.ui.toDoubleSpinBox.setMaximum(1000000)
        self.ui.fromDoubleSpinBox.setMaximum(1000000)

        self.ui.toDoubleSpinBox.setMinimum(-1000000)
        self.ui.fromDoubleSpinBox.setMinimum(-1000000)

        self.ui.xMultiplier.setMaximum(100000000)
        self.ui.yMultiplier.setMaximum(100000000)

        self.ui.xMultiplier.setDecimals(5)
        self.ui.yMultiplier.setDecimals(5)

        self.ui.xD.setMaximum(100000000)
        self.ui.yD.setMaximum(100000000)

        self.ui.xD.setDecimals(5)
        self.ui.yD.setDecimals(5)

        self.ui.gridLayout.replaceWidget(self.ui.xAxisName, self.XComboBox)
        self.ui.xAxisName.deleteLater()
        self.ui.xAxisName.hide()
        self.ui.xAxisName = None

        self.ui.gridLayout_2.replaceWidget(self.ui.yAxisName, self.YComboBox)
        self.ui.yAxisName.deleteLater()
        self.ui.yAxisName.hide()
        self.ui.yAxisName = None

        self.ui.formLayout_5.replaceWidget(self.ui.comboBox, self.ZComboBox)
        self.ui.comboBox.deleteLater()
        self.ui.comboBox.hide()
        self.ui.comboBox = None

    def init_values(self, project_id):


        self.project_id = project_id
        curve_list = utils_.get_project_param_names(project_id)
        self.curves = {name: None for name in curve_list}
        self.ZComboBox.addItems(curve_list)
        self.XComboBox.addItems(curve_list)
        self.YComboBox.addItems(curve_list)
        self._set_axis_combo_value(self.XComboBox, self.x_label)
        self._set_axis_combo_value(self.YComboBox, self.y_label)

    @staticmethod
    def _set_axis_combo_value(combo_box, value):
        if value and combo_box.findText(value) == -1:
            combo_box.addItem(value)
        combo_box.setCurrentText(value or '')

    def _ensure_param_values(self, param_name):
        if not param_name or param_name in self.param_values:
            return
        _curves = utils_.get_param_values(self.project_id, param_name)
        for _c in _curves:
            c_val = to_float(_c.value)
            if _c.param not in self.param_values.keys():
                self.param_values[_c.param] = Values(c_val, c_val)
            if c_val > self.param_values[_c.param].max_val:
                self.param_values[_c.param].max_val = c_val
            if c_val < self.param_values[_c.param].min_val:
                self.param_values[_c.param].min_val = c_val

    def manually_checked(self):
        self.ui.xGridManually.setChecked(True)
        self.ui.yGridManually.setChecked(True)

    def x_grid_man_clicked(self):
        self.ui.xMajor.setFocus()
        self.ui.yGridManually.setChecked(True)

    def y_grid_man_clicked(self):
        self.ui.yMajor.setFocus()
        self.ui.xGridManually.setChecked(True)

    def x_grid_auto_clicked(self):
        self.ui.xMajor.clearFocus()
        self.ui.yGridAuto.setChecked(True)

    def y_grid_auto_clicked(self):
        self.ui.yMajor.clearFocus()
        self.ui.xGridAuto.setChecked(True)

    def refresh(self):
        """Функция обновления значений и перепиривязки настроек графифической области."""
        plotview = self.plotview

        # Выставляем полученные параметры в поля диалогового окна
        self.ui.plotName.setText(plotview.graph_name)

        self._set_axis_combo_value(self.XComboBox, self.x_label)
        self._set_axis_combo_value(self.YComboBox, self.y_label)

        # TODO не записывать None в LineEdit
        self.ui.xMin.setText(plotview.graph_left_x)
        self.ui.xMax.setText(plotview.graph_right_x)
        self.ui.yMin.setText(plotview.graph_bottom_y)
        self.ui.yMax.setText(plotview.graph_top_y)

        self.ui.xAxisFixed.setChecked(to_bool(plotview.graph_fixed_x))
        self.ui.yAxisFixed.setChecked(to_bool(plotview.graph_fixed_y))

        # self.ui.fixedPoints.setChecked(fixed_points)  # TODO добавить фиксированные и динамические точки

        self.ui.xMajor.setValue(to_float(plotview.graph_x_major_step))
        self.ui.xMinor.setValue(to_float(plotview.graph_x_minor_step) if plotview.graph_x_minor_step else 0.0)

        self.ui.yMajor.setValue(to_float(plotview.graph_y_major_step))
        self.ui.yMinor.setValue(to_float(plotview.graph_y_minor_step) if plotview.graph_y_minor_step else 0.0)

        self.ui.xMultiplier.setValue(float(plotview.graph_x_multiplier))
        self.ui.yMultiplier.setValue(float(plotview.graph_y_multiplier))

        self.ui.xD.setValue(float(plotview.graph_x_dultiplier))
        self.ui.yD.setValue(float(plotview.graph_y_dultiplier))

        self.ui.lineEdit.setText('' if plotview.graph_x_comment is None else plotview.graph_x_comment)
        self.ui.lineEdit_2.setText('' if plotview.graph_y_comment is None else plotview.graph_y_comment)

        if to_bool(plotview.graph_x_step_auto):
            self.ui.xGridAuto.setChecked(True)
        else:
            self.ui.xGridManually.setChecked(True)

        if to_bool(plotview.graph_y_step_auto):
            self.ui.yGridAuto.setChecked(True)
        else:
            self.ui.yGridManually.setChecked(True)
        if hasattr(self.plotview, 'graph_constraints'):
            self.init_constraints()

    def init_constraints(self):
        param_constraints = json.loads(self.plotview.graph_constraints)
        if param_constraints:
            for pc in param_constraints:
                self.ui.listWidget.addItem(pc)
                if pc in self.param_values:
                    self.param_values[pc].max_val = param_constraints[pc]['max']
                    self.param_values[pc].min_val = param_constraints[pc]['min']

            self.ZComboBox.setCurrentText(list(param_constraints.keys())[0])
            self.update_values()

    def step_tuple(self, axis):
        """Возвращает множество для отображения шагов. Axis может иметь значение 'x' или 'y' """
        if axis == 'x':
            major, minor = self.ui.xMajor.value(), self.ui.xMinor.value()
        elif axis == 'y':
            major, minor = self.ui.yMajor.value(), self.ui.yMinor.value()
        # Заменяем 0.0 на None
        return major, minor

    def check_fields(self):
        if self.ui.xGridManually.isChecked():
            if not self.ui.xMinor.value() or not self.ui.xMajor.value():
                return False, 'Шаг сетки не может быть равен 0 (X).'
        if self.ui.yGridManually.isChecked():
            if not self.ui.yMinor.value() or not self.ui.yMajor.value():
                return False, 'Шаг сетки не может быть равен 0 (Y).'
        return True, ''

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

    def apply(self):
        # success, message = self.check_fields()
        # if not success:
        #     basic_funcs.error('Ошибка при заполнении полей зньачений', message)
        #     return

        """Возвращаем выбранные настроки графической области по нажатию на ОК."""
        plotview = self.plotview
        old_x = plotview.graph_label_x
        old_y = plotview.graph_label_y
        new_x = self.XComboBox.currentText()
        new_y = self.YComboBox.currentText()

        plotview.graph_name = self.ui.plotName.text()
        plotview.graph_label_x = new_x
        plotview.graph_label_y = new_y
        plotview.graph_left_x = self.ui.xMin.text()
        plotview.graph_right_x = self.ui.xMax.text()
        plotview.graph_bottom_y = self.ui.yMin.text()
        plotview.graph_top_y = self.ui.yMax.text()
        plotview.graph_fixed_x = self.ui.xAxisFixed.isChecked()
        plotview.graph_fixed_y = self.ui.yAxisFixed.isChecked()

        plotview.graph_x_multiplier = self.ui.xMultiplier.value()
        plotview.graph_y_multiplier = self.ui.yMultiplier.value()
        plotview.graph_x_dultiplier = self.ui.xD.value()
        plotview.graph_y_dultiplier = self.ui.yD.value()
        x_major, x_minor = self.step_tuple('x')
        plotview.graph_x_major_step = x_major
        plotview.graph_x_minor_step = x_minor

        y_major, y_minor = self.step_tuple('y')
        plotview.graph_y_major_step = y_major
        plotview.graph_y_minor_step = y_minor

        plotview.graph_x_step_auto = self.ui.xGridAuto.isChecked()
        plotview.graph_y_step_auto = self.ui.yGridAuto.isChecked()

        plotview.graph_x_comment = self.ui.lineEdit.text()
        plotview.graph_y_comment = self.ui.lineEdit_2.text()

        plotview.graph_group_by = self.get_group_by()
        plotview.graph_constraints = self.get_constraints()

        self.axis_params_changed = old_x != new_x or old_y != new_y
        if self.axis_params_changed:
            graph_id = getattr(getattr(plotview, '_data', None), 'id', None)
            logger.info(
                'Graph axis params changed: graph_id=%s, old_x=%s, old_y=%s, new_x=%s, new_y=%s',
                graph_id, old_x, old_y, new_x, new_y,
            )

        self.res = plotview
        self.plotview.update_db_props()
        # Закрываем окно
        self.accept()
