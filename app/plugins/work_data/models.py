from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from app import basic_funcs
from app.plugins.base_state.models import Node, TreeModel
from db import sp
from db.tables import PRODUCT
from db.transactions import import_file_data, delete_file_data, import_other_file_data


class WorkDataNode(Node):
    """Корень дерева справочника изделий"""
    scheme = PRODUCT

    def __init__(self, data):

        super().__init__(data)

    @staticmethod
    def internal_type():
        return 'root'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, ProductNode, FileNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_product(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def restore(item):
        success = sp.delete_product(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success

    @staticmethod
    def update(item, prop_name, prop_value):
        data = item._data
        data.prod_prop = prop_name
        data.prod_prop_value = prop_value
        project_record = data.table_fit(PRODUCT)
        item = sp.new_update_product_from_record(project_record)
        if item:
            return item


class FileNode(WorkDataNode):
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
            new_product = import_other_file_data(filename, file, 7, up_node_id)
            if new_product:
                result_items += [FileNode(new_product)]
        return tuple(result_items)

    @staticmethod
    def remove(item, final=False):
        if final:
            success = delete_file_data(item._data.id, 'other', other_format=True)
        else:
            success = sp.delete_product(item._data.id, True, True, False)

        if success:
            item._data.deleted = True
        return success


class FolderNode(WorkDataNode):
    """Узел-папка"""
    exclude_from_base_actions = ['_open']

    @staticmethod
    def internal_type():
        return 'folder'

    @staticmethod
    def is_folder():
        """Является ли элемент папкой"""
        return True

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (папка)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (папка)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, ProductNode, ModelNode, AssemblyNode, TestNode, FileNode]

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/folder.png")

    @staticmethod
    def add(up_node_id, parent):
        product_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not product_name:
            return
        product = (None, None, up_node_id, 6, 'name', product_name, None, 0, None)
        new_product = sp.new_update_product_from_record(product)
        new_product.type_ = 'folder'
        return FolderNode(new_product)


class ProductNode(WorkDataNode):
    """Узел-изделие"""

    @staticmethod
    def internal_type():
        return 'product'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, ModelNode, FileNode]

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/product.png")

    @staticmethod
    def add(up_node_id, parent):
        product_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not product_name:
            return
        product = (None, None, up_node_id, 2, 'name', product_name, None, 0, None)
        new_product = sp.new_update_product_from_record(product)
        new_product.type_ = 'product'
        return ProductNode(new_product)


class ModelNode(WorkDataNode):
    """Узел-модель"""

    @staticmethod
    def internal_type():
        return 'model'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (модель)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, AssemblyNode, FileNode]

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/model.png")

    @staticmethod
    def add(up_node_id, parent):
        product_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not product_name:
            return
        product = (None, None, up_node_id, 3, 'name', product_name, None, 0, None)
        new_product = sp.new_update_product_from_record(product)
        new_product.type_ = 'model'
        return ModelNode(new_product)


class AssemblyNode(WorkDataNode):
    """Узел-сборка"""

    @staticmethod
    def internal_type():
        return 'assembly'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (сборка)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, TestNode, FileNode]

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/assembly.png")

    @staticmethod
    def add(up_node_id, parent):
        product_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not product_name:
            return
        product = (None, None, up_node_id, 4, 'name', product_name, None, 0, None)
        new_product = sp.new_update_product_from_record(product)
        new_product.type_ = 'assembly'
        return AssemblyNode(new_product)


class TestNode(WorkDataNode):
    """Узел-испытание"""

    @staticmethod
    def internal_type():
        return 'test'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (испытание)"""
        return []

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (испытание)"""
        # return ['export', 'remove', 'version_control']
        return ['remove', 'version_control']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/test.png")

    def data(self, column=0):
        return self.name + f' - Версия {getattr(self, "final_version", 0)}'

    @staticmethod
    def _get_main_window():
        active_window = QApplication.activeWindow()
        if active_window and hasattr(active_window, 'run_with_progress'):
            return active_window

        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'run_with_progress'):
                return widget

        return None

    @staticmethod
    def add(up_node_id, parent):
        files = basic_funcs.get_files("Открытие исходных файлов Excel", "Файл Microsoft Excel (*.xls *.xlsx)",
                                      single_selection=False)
        result_items = []
        main_window = TestNode._get_main_window()
        for file in files:
            def run_import(import_file=file):
                return import_file_data(import_file.split('/')[-1], import_file, up_node_id)

            if main_window and hasattr(main_window, 'run_with_progress'):
                result = main_window.run_with_progress(
                    run_import,
                    progress_text='Импорт рабочих данных',
                )
            else:
                result = run_import()

            if isinstance(result, Exception):
                raise result

            new_product, version = result
            if new_product:
                new_product.type_ = 'test'
                result_items += [TestNode(new_product), TestNode(version)]
        return tuple(result_items)

    @staticmethod
    def remove(item, final=False):
        if final:
            success = delete_file_data(item._data.id, 'input_excel')
        else:
            success = sp.delete_product(item._data.id, True, True, False)

        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def export(item):
        pass


class WorkDataTreeModel(TreeModel):
    """Дерево справочника изделий"""

    def __init__(self):
        super().__init__()
        self._root = WorkDataNode(None)  # переопределяем корень
        # связать тип элемента с классом в программе
        self.register_nodes([WorkDataNode, FolderNode, ProductNode, ModelNode, AssemblyNode, TestNode, FileNode])
