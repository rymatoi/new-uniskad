from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QIcon

from app.basic_funcs import get_text
from app.plugins.base_state.models import Node, TreeModel
from db import sp
from db.schemas import SpravName


class DictionaryNode(Node):
    """Корень дерева первичных данных"""
    exclude_from_base_actions = ['_customize', '_rename_node']
    @staticmethod
    def internal_type():
        return 'root'

    def columnCount(self):
        return 2

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [ConfirmedNodes, UnconfirmedNodes]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def data(self, column=0):
        """То, что отображается в названии узла"""
        if column == 0:
            return self._data.param_name
        if self._data.eizm_short == 'not_set':
            return None
        return self._data.eizm_short


class ConfirmedNodes(DictionaryNode):
    exclude_from_base_actions = ['_open', '_remove', '_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'confirmed_nodes'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [StandardNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    def data(self, column=0):
        """То, что отображается в названии узла"""
        if column == 0:
            return 'Подтвержденные'

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(':/folder.png')


class UnconfirmedNodes(DictionaryNode):
    exclude_from_base_actions = ['_open', '_remove', '_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'unconfirmed_nodes'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [UnconfirmedNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def data(self, column=0):
        """То, что отображается в названии узла"""
        if column == 0:
            return 'Неподтвержденные'

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(':/folder.png')


class StandardNode(DictionaryNode):
    """Эталон"""
    exclude_from_base_actions = ['_remove', '_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'standard'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [SynonymNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['unconfirm']

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/alpha.png")

    @staticmethod
    def add(up_node_id, parent):
        item_name = get_text('Создание параметра', 'Название нового параметра эталона:')
        if not item_name:
            return
        param_id = sp.new_sprav_names_record((
            0, item_name, 0, False, True, '', 0, 2
        ))
        if param_id < 0:
            return
        else:
            return StandardNode(SpravName(
                {
                    'id_name': param_id,
                    'param_name': item_name,
                    'id_permanent_name': up_node_id,
                    'type_': 'standard'
                }
            ))


class UnconfirmedNode(DictionaryNode):
    """Неподтвержденный элемент"""

    exclude_from_base_actions = ['_remove', '_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'unknown'

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
        """Список действий с данным элементом (корень дерева)"""
        return ['confirm']

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/warning-alpha.png")


class SynonymNode(DictionaryNode):
    """Синоним"""
    exclude_from_base_actions = ['_remove', '_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'synonym'

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
        """Список действий с данным элементом (корень дерева)"""
        return ['unconfirm']

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/beta.png")

    @staticmethod
    def add(up_node_id, parent):
        item_name = get_text('Создание параметра', 'Название нового параметра синонима:')
        if not item_name:
            return
        param_id = sp.new_sprav_names_record((
            0, item_name, 0, True, True, '', up_node_id, 2
        ))
        if param_id < 0:
            return
        else:
            return SynonymNode(SpravName(
                {
                    'id_name': param_id,
                    'param_name': item_name,
                    'id_permanent_name': up_node_id,
                    'type_': 'synonym'
                }
            ))


class SynonymDictionaryTreeModel(TreeModel):
    """Дерево справочника изделий"""
    headers = ["Название", "ед. изм."]

    def __init__(self):
        super().__init__()
        self._root = DictionaryNode(None)  # переопределяем корень
        # связать тип элемента с классом в программе
        self.register_nodes([DictionaryNode, UnconfirmedNodes, ConfirmedNodes,
                             UnconfirmedNode, StandardNode, SynonymNode])
        self.root_id = None

    def confirm_parameter(self, node):
        confirmed_nodes = self._root.child(0)
        confirmed_nodes_index = self.index(0, 0, QModelIndex())
        if node._data.flag_synonim:
            for standard in confirmed_nodes._children:
                if node._data.id_permanent_name == standard._data.id_name:
                    parent = self.index(standard.row(), 0, confirmed_nodes_index)
                    self.addChild(node, parent)
                    self.dataChanged.emit(parent, parent)
                    break
        else:
            self.addChild(node, confirmed_nodes_index)
            self.dataChanged.emit(confirmed_nodes_index, confirmed_nodes_index)

    def unconfirm_parameter(self, node):
        new_node = UnconfirmedNode(node._data.attrs_update({
            'flag_synonim': False,
            'flag_permanent': False,
            'type_': 'unknown'
        }))
        unconfirmed_nodes_index = self.index(1, 0, QModelIndex())
        self.insertChild(new_node, unconfirmed_nodes_index, 0)
        self.dataChanged.emit(unconfirmed_nodes_index, unconfirmed_nodes_index)

    def remove_parameter(self, node):
        parent_item = node.parent()
        parent = self.createIndex(parent_item.row(), 0, parent_item)
        self.removeChild(node.row(), parent)
