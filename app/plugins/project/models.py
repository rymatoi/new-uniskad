import json
from copy import copy
from datetime import datetime

from PySide2.QtGui import QIcon, Qt

from app import basic_funcs
from app.plugins.base_state.models import TreeModel, Node, ANY_CHILD_TYPE
from app.plugins.project import utils
from app.plugins.project.dialogs.create_epure import CreateEpureDialog
from app.plugins.project.dialogs.create_graph import CreateGraphDialog
from app.plugins.project.dialogs.edit_epure import EditEpureDialog
from app.plugins.project.dialogs.select_test import TestSelectionDialog
from app.plugins.project.dialogs.select_test_data import TestDataSelectionDialog
from app.plugins.project.dialogs.test_edit import EditProjectItemDialog
from app.plugins.project.utils_ import get_next_default_combination
from app.plugins.work_data.models import ProductNode, ModelNode, AssemblyNode
from db import sp
from db.tables import PROJECT_TABLE, PROJECT_DATA
from db.transactions import import_project_other_file_data, \
    delete_file_data_project


class ProjectRoot(Node):
    """Корень дерева первичных данных"""

    def __init__(self, data):
        super().__init__(data)
        self.scheme = PROJECT_TABLE

        self.curve_name = None
        self.curve_width = None
        self.curve_color = None
        self.curve_line_style = None
        self.curve_point_symbol = None
        self.curve_point_size = None

        self.curve_point_size = None
        self.curve_symbol_color = None
        self.curve_symbol_fill_color = None

        self.selected_curve_point_size = 0.5
        self.selected_curve_symbol_color = 'black'
        self.selected_curve_symbol_fill_color = 'red'

        self.selected_points = None

        self.display_as_curve = True
        self.use_conditions = False
        self.use_filters = False
        self.conditions = None
        self.filters = None

        self.graph_x_comment = None
        self.graph_y_comment = None

    _project_types_cache = None

    @staticmethod
    def internal_type():
        return 'root'

    def columnCount(self):
        return 1

    @classmethod
    def get_project_type_id(cls, type_name):
        if cls._project_types_cache is None:
            cls._project_types_cache = {
                project_type.project_type: project_type.id_project_type
                for project_type in sp.get_projecttypes_list()
            }
        return cls._project_types_cache.get(type_name)

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def update(item, prop_name, prop_value):
        """
        Обновление элементов проекта
        :param item:
        :param prop_name:
        :param prop_value:
        :return:
        """
        data = item._data
        data.project_prop = prop_name
        data.project_prop_value = prop_value
        project_record = data.table_fit(PROJECT_TABLE)
        item = sp.new_update_project_from_record(project_record)
        if item:
            return item

    @staticmethod
    def bulk_update(item, props):
        item = sp.new_update_project_from_record_array(props)

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class ProjectNode(ProjectRoot):

    @staticmethod
    def internal_type():
        return 'project'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [TestNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/project_copy.png")


class FolderNode(ProjectRoot):

    @staticmethod
    def internal_type():
        return 'folder'

    @staticmethod
    def is_folder():
        return True

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [ANY_CHILD_TYPE]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    @staticmethod
    def add(up_node_id, parent):
        folder_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not folder_name:
            return
        folder_name = folder_name.strip()
        if not folder_name:
            return

        folder_type_id = ProjectRoot.get_project_type_id('folder')
        if folder_type_id is None:
            basic_funcs.error('Ошибка', 'Не удалось определить тип "folder".')
            return

        parent_data = getattr(parent, '_data', None)
        project_author = getattr(parent_data, 'project_author', None)
        project_owner = getattr(parent_data, 'project_owner', None)

        record = (
            None,
            None,
            up_node_id,
            folder_type_id,
            'name',
            folder_name,
            project_author,
            project_owner,
            datetime.now(),
            0,
            False,
        )

        new_folder = sp.new_update_project_from_record(record)
        if new_folder:
            new_folder.type_ = 'folder'
            return FolderNode(new_folder)

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class ProductFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'product_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [TestNode, FileNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'import']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class GraphFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'graph_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [GraphNode, FileNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'save_graph_template', 'apply_graph_template']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class EpureFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'epure_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [EpureNode, FileNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'save_epure_template', 'apply_epure_template']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class WDAssemblyNode(AssemblyNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        success = sp.delete_project(item._data.id, True, False, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.find_parent_by_internal_type('product_folder')
            if parent is None:
                return self

            root = parent.parent()
            if root is None:
                return self
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, False, cascade, False)
        if success:
            item._data.deleted = False
        return success


class WDModelNode(ModelNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.find_parent_by_internal_type('product_folder')
            if parent is None:
                return self

            root = parent.parent()
            if root is None:
                return self
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class WDProductNode(ProductNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.find_parent_by_internal_type('product_folder')
            if parent is None:
                return self

            root = parent.parent()
            if root is None:
                return self
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class TestNode(ProjectRoot):
    has_customization = True

    def __init__(self, data):

        super().__init__(data)
        self.param_sort_setting = None
        self.default_values = False

    @staticmethod
    def internal_type():
        return 'test'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        # return ['export', 'remove']
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/test.png")

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.find_parent_by_internal_type('product_folder')
            if parent is None:
                return self

            root = parent.parent()
            if root is None:
                return self
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            epure_folder = [folder for folder in root.children if folder.internal_type() == 'epure_folder']
            if len(graph_folder) == 1 and len(epure_folder) == 1:
                return tuple([child for child in graph_folder[0].children + epure_folder[0].children if
                              child._data.deleted is False] + [self])
            return self

    @staticmethod
    def add(up_node_id, parent):
        dialog = TestSelectionDialog()
        if dialog.exec_():
            project_types = {}
            project_types_reversed = {}  # TODO придумать как тут ускорить
            for project_type in sp.get_projecttypes_list():
                project_types[project_type.project_type] = project_type.id_project_type
                project_types_reversed[project_type.id_project_type] = project_type.project_type

            def new_prop(data, prop_name, prop_value):
                prop = copy(data)
                prop.project_prop = prop_name
                prop.project_prop_value = str(prop_value)
                return prop

            class_dict = {
                'test': TestNode,
                'assembly': WDAssemblyNode,
                'model': WDModelNode,
                'product': WDProductNode,
                'folder': FolderNode,
                'file': FileNode,
            }

            selected = dialog.get_result()
            current_item = selected[0]
            while current_item.parent() in selected:
                current_item = current_item.parent()
            selected_data = []
            selected_props_data = []
            parent_id = current_item._data.id_up_prod

            for obj in selected:
                if not any(obj._data.id_up_prod == other_obj._data.id_prod for other_obj in selected if
                           obj != other_obj):
                    obj._data.id_up_prod = parent_id

            project_node = parent.parent()

            if hasattr(project_node, 'default_test_value'):
                next_default_value = int(project_node.default_test_value) + 1
            else:
                next_default_value = 0

            for product in selected:
                product_data = product._data
                product_data.project_id = product_data.id_prod
                product_data.project_id_up = product_data.id_up_prod
                product_data.project_type = project_types[product.internal_type()]
                product_data.project_prop = product_data.prod_prop
                product_data.project_prop_value = product_data.prod_prop_value
                selected_data.append(product_data.table_fit(PROJECT_TABLE))

                if product.internal_type() == 'file':
                    pass  # TODO не работает импорт файлов из рабочих данных

                if product.internal_type() == 'test':
                    next_default_value += 1
                    line_style, color, symbol = get_next_default_combination(next_default_value)
                    test_prop_data = copy(product_data)
                    test_prop_data.project_prop = 'test_id'
                    test_prop_data.project_prop_value = str(product_data.id)
                    selected_props_data.append(test_prop_data.table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_line_style', int(Qt.NoPen)).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_color', color).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_symbol_color', 'black').table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_symbol_fill_color', color).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_point_symbol', symbol).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_point_symbol', symbol).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_point_size', 10).table_fit(PROJECT_TABLE))

                    selected_props_data.append(
                        new_prop(product_data, 'curve_width', 1).table_fit(PROJECT_TABLE))

            sp.new_update_project_from_record(
                new_prop(project_node._data, 'default_test_value', next_default_value).table_fit(PROJECT_TABLE))
            result = sp.copy_tree_project_bunch(selected_data + selected_props_data, parent_id, up_node_id)
            result_mass = []
            test_projects = []
            for item in result:
                item.type_ = project_types_reversed[item.project_type]
                result_mass.append(class_dict[item.type_](item))
                if item.type_ == 'test' and item.prop_name == 'test_id':
                    test_projects.append(item)

            params = sp.get_param_list_from_test_id_list([int(item.prop_value) for item in test_projects])
            if not params:
                print('Не хватает данных.')
                return
            dialog = TestDataSelectionDialog(params)

            if dialog.exec_():
                res_data_rows = []
                param_list = dialog.get_result()

                def new_pr_prop(data, prop_name, prop_value):
                    prop = copy(data)
                    prop.param_prop_name = prop_name
                    prop.prop_value = str(prop_value)
                    return prop

                for test in test_projects:
                    param_data = sp.get_import_file_data_curves_data(int(test.prop_value), param_list)
                    for param in param_data:
                        param.project_id = test.project_id
                        if param.prop_name == 'type' and param.prop_value == 'row':
                            res_data_rows.append(
                                new_pr_prop(param, 'name', param.excel_param_name).table_fit(PROJECT_DATA))
                            if param.is_secret:
                                res_data_rows.append(
                                    new_pr_prop(param, 'is_secret', param.is_secret).table_fit(PROJECT_DATA))
                            if hasattr(param, 'eizm_short'):
                                res_data_rows.append(
                                    new_pr_prop(param, 'eizm_short', param.eizm_short).table_fit(PROJECT_DATA))
                        res_data_rows.append(param.table_fit(PROJECT_DATA))
                res_data_rows = sorted(res_data_rows, key=lambda x: x[0])
                sp.new_project_data_array(res_data_rows)
            return tuple(result_mass)

    @staticmethod
    def export(item):
        pass


class GraphNode(ProjectRoot):
    has_customization = False

    def __init__(self, data):
        super().__init__(data)

        self.graph_label_y = ''
        self.graph_label_x = ''
        self.graph_grid_size = 0

        self.graph_left_x = ''
        self.graph_right_x = ''
        self.graph_bottom_y = ''
        self.graph_top_y = ''
        self.graph_fixed_x = False
        self.graph_fixed_y = False
        self.graph_x_major_step = ''
        self.graph_x_minor_step = ''
        self.graph_y_major_step = ''
        self.graph_y_minor_step = ''
        self.graph_name = ''
        self.graph_x_step_auto = True
        self.graph_y_step_auto = True

        self.graph_group_by = ''
        self.graph_constraints = '{}'
        self.graph_appr_type = ''

        self.graph_x_multiplier = 1
        self.graph_y_multiplier = 1

        self.graph_x_dultiplier = 1
        self.graph_y_dultiplier = 1

    @staticmethod
    def internal_type():
        return 'graph'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/graph.png")

    @staticmethod
    def add(up_node_id, parent):
        project_item = parent.parent()
        dialog = CreateGraphDialog(project_item._data.id)
        if dialog.exec_():  # Если произошло изменение данных
            res = dialog.get_result()
            return GraphNode._add_graph(up_node_id, 'xy', f'{res["graph_name"]}', res["x_curve"], res["y_curve"],
                                        res["group_by"], res['constraints'])

    @staticmethod
    def _add_graph(up_node_id, graph_type, item_name, x_curve=None, y_curve=None, group_by=None, constraints=None):
        project_types = {}
        project_types_reversed = {}
        result = []
        result_mass = []

        for project_type in sp.get_projecttypes_list():
            project_types[project_type.project_type] = project_type.id_project_type
            project_types_reversed[project_type.id_project_type] = project_type.project_type

        if graph_type == 'xy':
            curves = sp.add_new_xy_graph(up_node_id, item_name, x_curve, y_curve, group_by, constraints)
            result = curves

        class_dict = {
            'graph': GraphNode
        }

        for item in result:
            item.type_ = project_types_reversed[item.project_type]
            result_mass.append(class_dict[item.type_](item))

        return tuple(result_mass)


class EpureNode(ProjectRoot):
    has_customization = True

    def __init__(self, data):
        super().__init__(data)

        self.graph_label_y = ''
        self.graph_label_x = ''
        self.graph_grid_size = 0

        self.graph_x_step_auto = True
        self.graph_y_step_auto = True

        self.graph_left_x = ''
        self.graph_right_x = ''
        self.graph_bottom_y = ''
        self.graph_top_y = ''
        self.graph_fixed_x = False
        self.graph_fixed_y = False
        self.graph_x_major_step = 0
        self.graph_x_minor_step = 0
        self.graph_y_major_step = 0
        self.graph_y_minor_step = 0
        self.graph_name = ''

        self.oy_list = None
        self.extra_param = None
        self.extra_param_values = None

        self.graph_x_multiplier = 1
        self.graph_y_multiplier = 1

        self.graph_x_dultiplier = 1
        self.graph_y_dultiplier = 1

    @staticmethod
    def internal_type():
        return 'epure'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/epure.png")

    def customize(self, ):
        project_item = self.parent().parent()
        dialog = EditEpureDialog(self, project_item, project_item._data.id, self.parent()._data.project_id)
        if dialog.exec_():
            return self

    @staticmethod
    def add(up_node_id, parent):
        project_item = parent.parent()
        dialog = CreateEpureDialog(project_item, project_item._data.id, up_node_id)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()
            for item in result:
                item.type_ = 'epure'
            return tuple(result)


class FileNode(ProjectRoot):
    """Узел-файл"""

    @staticmethod
    def internal_type():
        return 'file'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (модель)"""
        return []

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/file.png")

    @staticmethod
    def add(up_node_id, parent):
        files = basic_funcs.get_files("Открытие сторонних файлов", "* (*.*)",
                                      single_selection=False)
        result_items = []
        for file in files:
            filename = file.split('/')[-1][:30]
            new_product = import_project_other_file_data(filename, file, 19, up_node_id)
            if new_product:
                result_items += [FileNode(new_product)]
        return tuple(result_items)

    @staticmethod
    def remove(item, final=False):
        if not final:
            success = sp.delete_project(item._data.id, True, False, False)
            if success:
                item._data.deleted = True
            return success
        else:
            success = delete_file_data_project(item._data.id, 'other', other_format=True)
            return success


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


class ProjectTreeModel(TreeModel):
    """Дерево справочника изделий"""

    def __init__(self):
        super().__init__()
        self._root = ProjectRoot(None)  # переопределяем корень
        self.root_id = 1
        # связать тип элемента с классом в программе
        self.register_nodes(
            [ProjectRoot, ProjectNode, FolderNode, TestNode, GraphNode, EpureNode, EpureFolderNode,
             WDProductNode, WDModelNode, WDAssemblyNode, GraphFolderNode, ProductFolderNode, ParamNode, FileNode,
             ])

    def update_external_graphs(self):
        root = self._root
        graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
        epure_folder = [folder for folder in root.children if folder.internal_type() == 'epure_folder']
        if len(graph_folder) == 1 and len(epure_folder) == 1:
            self.view.update_external_nodes(
                tuple([child for child in graph_folder[0].children + epure_folder[0].children if
                       child._data.deleted is False]))
