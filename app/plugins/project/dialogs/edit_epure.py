import ast
from copy import copy

from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtGui import QIcon

from app import basic_funcs
from app.plugins.base_state.models import TreeModel, Node
from app.plugins.project import utils
from app.plugins.project.dialogs.OY_setup import OYSetupDialog
from app.plugins.project.dialogs.extra_param_epure import ExtraParamEpureDialog
from app.plugins.project.dialogs.select_project_test import ProjectTestSelectionDialog
from app.plugins.project.dialogs.select_test_data import TestDataSelectionDialog
from db import sp
from db.tables import PROJECT_TABLE
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_create_epure import Ui_CreateEpureDialog


class RowParam:
    type_ = 'param'
    id_up = 0
    id: str
    prop_name = 'name'
    prop_value: str
    base_name: str

    def __init__(self, data):
        self.id = data
        self.prop_value = data
        self.base_name = data


class ParamNode(Node):

    @staticmethod
    def internal_type():
        return 'param'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def get_icon(self, column=0):
        return QIcon(":/alpha.png")

    def data(self, column=0):
        return self._data.prop_value


class TestDataTreeModel(TreeModel):

    def __init__(self):
        super().__init__()
        self.CHECKABLE = False
        # self._root = ProjectRoot(None)  # переопределяем корень
        self.root_id = 0
        # связать тип элемента с классом в программе
        self.register_nodes([ParamNode])


class EditEpureDialog(BaseDialog):

    def __init__(self, item, project_item, project_id, up_node_id, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_CreateEpureDialog()
        self.folder_id = up_node_id
        self.project_id = project_id
        self.item = item
        self.project_item = project_item

        self.parameters = None

        self.param_list = ast.literal_eval(self.item.param_list)
        self.oy_list = self.item.oy_list
        self.extra_param = self.item.extra_param
        self.extra_param_values = self.item.extra_param_values

        self.ui.setupUi(self)
        self.model = TestDataTreeModel()  # Получение списка пользователей
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.paramsTreeView.setModel(self.proxy)

        self.selected_params = []
        self.selected_columns = []
        self.oy_list = []

        self.test_nodes = self.collect_tests()

        self.init_values()

        self.setWindowTitle('Настройка полей')

        self.create_connections()  # создаем привязки

    def init_values(self):
        params = [RowParam(param) for param in self.param_list]
        self.model.beginResetModel()
        self.model.ini_tree(params)
        self.model.endResetModel()
        self.selected_params += self.param_list

        self.ui.nameLineEdit.setText(self.item.name)
        self.ui.selectParam.setText(self.extra_param if self.extra_param else 'Выбрать параметр')
        self.ui.paramValuesLineEdit.setText(self.extra_param_values if self.extra_param else '')

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.addParamPushButton.clicked.connect(self.add_parameters)
        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.cancelPushButton.clicked.connect(self.close)
        self.ui.removeParamPushButton.clicked.connect(self.remove_param)
        self.ui.oySetupPushButton.clicked.connect(self.setup_oy)
        self.ui.selectParam.clicked.connect(self.select_extra_param)

    def select_extra_param(self):
        dialog = ExtraParamEpureDialog(self.test_nodes, self.project_id, self.extra_param, self.extra_param_values)
        if dialog.exec_():
            self.extra_param, self.extra_param_values = dialog.get_result()
            if self.extra_param is None:
                self.ui.selectParam.setText('Выбрать параметр')
                self.ui.paramValuesLineEdit.setText('')
            else:
                self.ui.selectParam.setText(self.extra_param)
                self.ui.paramValuesLineEdit.setText(str(self.extra_param_values))

    def collect_tests(self):
        test_folder = \
            [child for child in self.item.parent().parent().children if child.internal_type() == 'product_folder'][0]
        return self._inspect_children(test_folder, False)

    def _inspect_children(self, root, root_deleted):
        test_nodes = []
        for child in root.children:
            if child.internal_type() == 'test':
                if hasattr(child._data, 'deleted') and (
                        child._data.deleted == 'False' or child._data.deleted is False) and root_deleted is False:
                    test_nodes.append(child)
            else:
                if root_deleted:
                    test_nodes += self._inspect_children(child, True)
                elif child._data.deleted is True:
                    test_nodes += self._inspect_children(child, True)
                else:
                    test_nodes += self._inspect_children(child, False)
        return test_nodes

    def setup_oy(self):
        dialog = OYSetupDialog(self.selected_params)
        if dialog.exec_():
            self.oy_list = dialog.get_result()

    def check_name(self):
        if self.ui.nameLineEdit.text():
            return True
        return False

    def accept(self) -> None:
        prop_dict = {
            'name': self.ui.nameLineEdit.text(),
            'param_list': str(self.selected_params),
            'oy_list': str(self.oy_list),
            'extra_param': self.extra_param if self.extra_param is not None else '',
            'extra_param_values': str(self.extra_param_values),
        }

        for prop in self.item.obj_list:
            if prop.prop_name in prop_dict:
                prop.project_prop_value = prop_dict[prop.prop_name]
                setattr(self.item, prop.prop_name, prop_dict[prop.prop_name])
        if not self.check_name():
            basic_funcs.info('Пустое название элемента', 'Название не может быть пустым')
            return
        epure_with_props = sp.new_update_project_from_record_array(
            [obj.table_fit(PROJECT_TABLE) for obj in self.item.obj_list])
        self.res = epure_with_props
        super().accept()

    def remove_param(self):
        if indexes := self.ui.paramsTreeView.selectedIndexes():
            for index in indexes:
                self.model.removeChild(index.row(), index.parent())
                self.selected_params.pop(index.row())

    def add_parameters(self):
        self.parameters = utils.collect_project_params(sp.get_project_test_params(self.project_id))
        dialog = TestDataSelectionDialog(list(self.parameters.keys()))
        if dialog.exec_():
            params = [RowParam(param) for param in dialog.res]
            self.model.beginResetModel()
            self.model.ini_tree(params)
            self.model.endResetModel()
            self.selected_params += dialog.res

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
