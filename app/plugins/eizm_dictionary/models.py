from PySide2.QtWidgets import QDialog
from app.plugins.base_state.models import Node, TreeModel
from app.plugins.eizm_dictionary.dialogs.create_eizm import CreateEizmDialog
from db import sp


class EizmRootNode(Node):
    exclude_from_base_actions = ['_customize', '_rename_node']
    @staticmethod
    def internal_type():
        return 'root'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [EizmNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    def columnCount(self):
        return 2

    def data(self, column=0):
        """То, что отображается в названии узла"""
        if column == 0:
            return self._data.eizm_full
        return self._data.eizm_short


class EizmNode(EizmRootNode):
    """Единица измерения"""

    @staticmethod
    def internal_type():
        return 'eizm'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом"""
        return []

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['remove']

    @staticmethod
    def add(up_node_id, parent):
        dialog = CreateEizmDialog()
        if dialog.exec_() == QDialog.Accepted:
            eizm = dialog.get_result()
            node = EizmNode(eizm)
            return node

    @staticmethod
    def remove(item, final=False):
        success = sp.remove_sprav_eizm_record(item._data.id_eizm)
        return success


class EizmDictionaryTreeModel(TreeModel):
    """Дерево справочника изделий"""
    headers = ['Название', 'Сокращение']

    def __init__(self):
        super().__init__()
        self._root = EizmRootNode(None)  # переопределяем корень
        # связать тип элемента с классом в программе
        self.root_id = None
        self.register_nodes([EizmRootNode, EizmNode])
