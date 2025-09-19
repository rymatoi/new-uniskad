from copy import copy
from typing import List
import PySide2
from PySide2.QtCore import QAbstractItemModel, QPointF, Signal
from PySide2.QtGui import QIcon, QFont, QColor, QPainter, QPen, QPixmap

from PySide2.QtCore import Qt, QModelIndex

replace_dict = {
    'True': True,
    'False': False
}


class Node(object):
    """Базовая модель узла"""

    exclude_from_base_actions = []  # _open, _customize
    has_customization = False
    scheme = None

    def __init__(self, data, parent_widget=None):
        self.parent_widget = parent_widget

        self._data = data
        self._parent = None
        self._children = []

        self.obj_list = []

        # сторонние свойства
        self.font_bold = False
        self.font_name = None
        self.font_size = None
        self.font_underline = False
        self.font_italic = False
        self.font_strikeout = False
        self.font_bgcolor = None
        self.font_text_color = None
        self.icon = None

        self.checked = False
        self._checked_count = 0

        self.name = None

    @staticmethod
    def internal_type():
        """Тип узла дерева. Служит для связи объекта
         из базы данных и узла дерева в программе.
         (поле type_ в schemes.py это internal_type() узла дерева)"""
        return 'node'

    @property
    def children(self):
        return self._children

    @staticmethod
    def is_folder():
        return False

    @staticmethod
    def container_types():
        """Возможные дочерние элементы узла."""
        return []

    def is_checked(self):
        """Условие наличия галочки"""
        return self.checked

    def check(self, state):
        """Установка галочки/снятие галочки"""
        self.checked = state

    @staticmethod
    def internal_actions() -> List[str]:
        """Действия с дочерними элементами узла."""
        return []
        # internal_actions: ['add'],
        # container_types: ['standard', 'synonym']
        # ---
        # actions: ['_add_standard', '_add_synonym', '_add']

    @staticmethod
    def self_internal_actions() -> List[str]:
        """Действия с самим узлом."""
        return []
        # internal_actions: ['remove']
        # internal_type: 'product'
        # ---
        # actions: ['_remove', '_remove_product']

    def get_icon(self, column=0):
        if getattr(self._data, 'icon', None):
            return QIcon(self._data.icon)
        return None

    def data(self, column=0):
        if self.name:
            return self.name
        return self._data.prop_name

    def columnCount(self):
        return 1

    def childCount(self):
        return len(self._children)

    def checked_children_count(self):
        return [child for child in self._children if child.is_checked()]

    def child(self, row):
        if 0 <= row < self.childCount():
            return self._children[row]

    def row(self):
        if self._parent:
            return self._parent._children.index(self)
        return 0

    def insertChildren(self, position, items):
        for item in items:
            item._parent = self
            self._children.insert(position, item)

    def addChild(self, child):
        child._parent = self
        self._children.append(child)

    def removeChild(self, row: int):
        """Удалить дочерний элемент по его номеру"""
        try:
            self._children[row]._parent = None
            self._children.pop(row)
        except IndexError:
            pass

    def parent(self):
        return self._parent

    def customize(self):
        pass
        # info('Изменение элемента', 'Изменение данного элемента из дерева не предусмотрено.')

    @staticmethod
    def add(up_node_id, parent):
        pass

    @staticmethod
    def remove(item, final=False):
        pass

    @staticmethod
    def restore(item):
        pass

    @staticmethod
    def update(item, prop_name, prop_value):
        pass

    @staticmethod
    def bulk_update(item, props):
        pass

    @staticmethod
    def export(item):
        pass

    def update_class_props(self, props: list):
        for prop in props:
            if prop.prop_name:
                setattr(self, prop.prop_name, prop.prop_value)

    # def update_class_props(self, props: list):
    #     for prop in self.obj_list:
    #         for _prop in props:
    #             if prop.prop_name == _prop.prop_name:
    #                 self.obj_list.remove(prop)
    #                 self.obj_list.append(_prop)
    #         setattr(self, prop.prop_name, prop.prop_value)

    def update_db_props(self):
        props = []
        for prop in self.__dict__:
            if prop.startswith(f'{self.internal_type()}_'):
                prop_scheme = copy(self._data)
                prop_scheme.set_val('id_record', None)
                prop_scheme.set_val('prop_name', prop)
                prop_scheme.set_val('prop_value', '' if getattr(self, prop) is None else str(getattr(self, prop)))
                props.append(prop_scheme.table_fit(self.scheme))
        self.bulk_update(self, props)


class TreeModel(QAbstractItemModel):
    """Базовая модель дерева"""

    itemChecked = Signal(object)
    headers = ["Название"]
    CHECKABLE = False

    def __init__(self, parent_widget=None):
        super().__init__()
        self.view = None
        self.parent_widget = parent_widget
        self._root = Node(None)
        self.action_types = {}  # словарь предназначен для хранения действий над дочерними элементами узлов
        self.self_action_types = {}  # словарь предназначен для хранения действий нам самими узлами
        self.item_types = {  # связь типов элементов с классами в программе
            'root': Node
        }
        self.display_prop = 'name'
        self.root_id = 0
        self.checked_list = []
        self._prop_dict = {}

        self.font_name = 'Times New Roman'
        self.font_size = 14

        # self.register_nodes()

    def get_root_elements(self):
        root_elements = []

        # Iterate over all rows in the model
        for row in range(self.rowCount()):
            # Get the index of each item in the first column
            index = self.index(row, 0)

            # Use the parent() method to check if it has a valid parent
            if index.parent().isValid():
                root_elements.append(index)

        return root_elements

    def set_view(self, view):
        self.view = view

    def register_data_nodes(self, type_list=None):
        self.register_nodes(type_list)

    def register_nodes(self, type_list=None):
        """Формируем словарь действий для узлов на основе internal_actions и self_internal_actions.
         Ключ - тип элемента, значение - список действий.
        type_list - перечисление всех возможных узлов дерева.
        """
        if type_list:
            self.item_types.update({node.internal_type(): node for node in type_list})
        for k, v in self.item_types.items():
            self.action_types.setdefault(v, set())
            self.self_action_types.setdefault(v, set())
            for action in v.internal_actions():
                self.action_types[v].add(f'_{action}')
                for child_node in v.container_types():
                    self.action_types[v].add(f'_{action}_{child_node.internal_type()}')
            for action in v.self_internal_actions():
                self.self_action_types[v].add(f'_{action}')
                self.self_action_types[v].add(f'_{action}_{v.internal_type()}')

    def preprocess_nodes(self, nodes):
        """
        Создает словарь, где ключ — id_up, а значение — список дочерних узлов.
        """
        from collections import defaultdict
        children_dict = defaultdict(list)
        for node in nodes:
            children_dict[node.id_up].append(node)
        return children_dict

    def ini_tree(self, nodes, display_prop='name'):
        """
        Инициализация дерева: подготавливает данные и вызывает построение дерева.
        """
        self.display_prop = display_prop
        self._setup_props(nodes)

        # Предобработка узлов для быстрого доступа к дочерним элементам
        children_dict = self.preprocess_nodes(nodes)

        # Запуск построения дерева
        self.__ini_tree(children_dict, self.root_id, self._root)

    def custom_ini_tree(self, nodes, root_id, root_item, root_item_index=None):
        children_dict = self.preprocess_nodes(nodes)
        self.__ini_tree(children_dict, root_id, root_item, root_item_index)

    def __ini_tree(self, children_dict, root_id, root_item, root_item_index=None):
        """
        Итеративное построение дерева с учётом root_item_index.
        """
        # Стек для обхода узлов (каждый элемент: текущий узел, родительский элемент дерева и индекс)
        stack = [(root_id, root_item, root_item_index)]

        # Итеративное построение дерева
        while stack:
            current_id, parent_item, parent_index = stack.pop()

            # Получаем дочерние элементы текущего узла
            child_nodes = children_dict.get(current_id, [])
            for node in child_nodes:
                if node.prop_name != self.display_prop:
                    continue

                # Создаем элемент узла
                element_item = self.item_types.get(node.type_, self.item_types['root'])(node)

                # Добавляем элемент в дерево
                if parent_index is not None:
                    self.insertRows(parent_item.childCount(), [element_item], parent_index)
                else:
                    parent_item.addChild(element_item)

                # Обрабатываем свойства элемента
                props = self._prop_dict.setdefault(node.id, [])
                for prop in props:
                    element_item.obj_list.append(prop)
                    setattr(element_item, prop.prop_name, prop.prop_value)

                # Добавляем дочерние элементы в стек для дальнейшей обработки
                stack.append((node.id, element_item, None))  # Индекс для детей не используется

    # def ini_tree(self, nodes, display_prop='name'):
    #     """
    #     Инициализация дерева с использованием оптимизации на основе предварительной обработки узлов.
    #     """
    #     self.display_prop = display_prop
    #     self._setup_props(nodes)
    #
    #     # Предобработка узлов для быстрого доступа к дочерним элементам
    #     self.children_dict = self.preprocess_nodes(nodes)
    #
    #     # Запуск построения дерева
    #     self._ini_tree(self.children_dict, self.root_id, self._root)
    #
    # def _ini_tree(self, children_dict, root, root_item, root_item_index=None):
    #     """
    #     Построение дерева с использованием словаря дочерних узлов.
    #     """
    #     # Получаем дочерние элементы для текущего узла
    #     root_elements = children_dict.get(root, [])
    #
    #     for element in root_elements:
    #         if element.prop_name != self.display_prop:
    #             continue
    #
    #         # Создаем элемент узла
    #         element_item = self.item_types.get(element.type_, self.item_types['root'])(element)
    #
    #         # Добавляем элемент в дерево
    #         if root_item_index:
    #             self.insertRows(root_item.childCount(), [element_item], root_item_index)
    #         else:
    #             root_item.addChild(element_item)
    #
    #         # Обрабатываем свойства элемента
    #         props = self._prop_dict.setdefault(element.id, [])
    #         for prop in props:
    #             element_item.obj_list.append(prop)
    #             setattr(element_item, prop.prop_name, prop.prop_value)
    #
    #         # Рекурсивно добавляем дочерние элементы (из словаря)
    #         child_items = children_dict.get(element.id, [])
    #         if child_items:
    #             self._ini_tree(children_dict, element.id, element_item)

    def _setup_props(self, nodes):
        """Собирает словарь со свойствами узла, где ключ - id элемента, а значение - список свойств"""
        for node in nodes:
            if node.id not in self._prop_dict:
                self._prop_dict[node.id] = []
            self._prop_dict[node.id].append(node)

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return self.nodeFromIndex(parent).childCount()

    def columnCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self._root.columnCount()

    def addChild(self, node, _parent):
        if not node._data.prop_name == self.display_prop:
            return
        parent = self.nodeFromIndex(_parent)
        self.insertRows(parent.childCount(), [node], _parent)
        props = self._prop_dict.get(node._data.id, [node._data])
        for prop in props:
            if prop.prop_value:
                setattr(node, prop.prop_name, prop.prop_value)

    def insertChild(self, node, _parent, row=0):
        self.insertRows(row, [node], _parent)

    def find_root_index(self):
        # Start from the first index in the model
        index = self.index(0, 0)

        # Traverse upwards until we find the root node (a node without a parent)
        while index.isValid():
            parent_index = index.parent()
            if not parent_index.isValid():
                # Found the root index
                return index
            index = parent_index

        # If we reach here, the model is empty or invalid
        return QModelIndex()

    def index(self, row, column, _parent=QModelIndex()):
        parent = self.nodeFromIndex(_parent)
        if not self.hasIndex(row, column, _parent):
            return QModelIndex()

        child = parent.child(row)
        if child:
            return self.createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if index.isValid():
            try:
                _parent = index.internalPointer().parent()
            except:
                print()
            if _parent:
                return self.createIndex(_parent.row(), 0, _parent)
        return QModelIndex()

    def headerData(self, section: int, orientation: PySide2.QtCore.Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.data(index.column())

        if role == Qt.ToolTipRole:
            return node.data()

        if role == Qt.BackgroundColorRole:
            if node.font_bgcolor:
                return QColor(node.font_bgcolor)
            else:
                return None

        if role == Qt.TextColorRole:
            return QColor(node.font_text_color)

        if role == Qt.DecorationRole:
            icon = node.get_icon(index.column())

            if hasattr(node._data, 'deleted') and node._data.deleted is True:
                # Get the pixmap from the icon
                pixmap = icon.pixmap(icon.actualSize(self.view.iconSize()))

                # Create a new pixmap for the modified icon
                pixmap_modified = QPixmap(pixmap.size())
                pixmap_modified.fill(Qt.transparent)

                # Draw the modified pixmap
                painter = QPainter(pixmap_modified)
                opacity = 0.5
                painter.setOpacity(opacity)
                painter.drawPixmap(pixmap.rect(), pixmap, pixmap.rect())
                painter.end()

                # Draw a red horizontal line on the modified pixmap
                pixmap_modified_rect = pixmap_modified.rect().adjusted(0, 0, -1, -1)
                painter = QPainter(pixmap_modified)
                pen = QPen(Qt.red, 2)
                painter.setPen(pen)
                painter.drawLine(QPointF(pixmap_modified_rect.left(), pixmap_modified_rect.center().y()),
                                 QPointF(pixmap_modified_rect.right(), pixmap_modified_rect.center().y()))
                painter.end()
                return QIcon(pixmap_modified)

            return icon

        if role == Qt.FontRole:
            font = QFont()
            if self.font_name:
                if not node.font_name:
                    font.setFamily(self.font_name)
                else:
                    font.setFamily(node.font_name)
            if self.font_size:
                if not node.font_size:
                    font.setPointSize(float(self.font_size))
                else:
                    font.setPointSize(float(node.font_size))
            else:
                font.setPixelSize(float(node.font_size))
            font.setBold(replace_dict.get(node.font_bold, node.font_bold))
            font.setUnderline(replace_dict.get(node.font_underline, node.font_underline))
            font.setItalic(replace_dict.get(node.font_italic, node.font_italic))
            font.setStrikeOut(replace_dict.get(node.font_strikeout, node.font_strikeout))
            return font

        if role == Qt.UserRole:
            if hasattr(node._data, 'deleted'):
                return node._data.deleted
            else:
                return False

        if self.CHECKABLE:
            if role == Qt.CheckStateRole and index.column() == 0:
                return node.is_checked()

    def moveItem(self, sourceIndex, destinationIndex):
        sourceRow = sourceIndex.row()
        destinationRow = destinationIndex.row()
        parentIndex = sourceIndex.parent()

        # Get items at source and destination positions
        sourceParentItem = parentIndex.internalPointer()
        sourceItem = sourceParentItem.child(sourceRow)

        # Remove item from source position
        sourceParentItem.removeChild(sourceRow)

        # Insert item at destination position
        sourceParentItem.insertChildren(destinationRow, [sourceItem])
        self.view.setCurrentIndex(destinationIndex)
        selection_model = self.view.selectionModel()
        selection_model.select(destinationIndex, selection_model.ClearAndSelect)

        # Emit dataChanged signal to update the view
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

    def setData(self, index: "QModelIndex", value: "Any", role: int = ...) -> bool:
        """Изменяет данные на интерфейсе"""
        if index.column() == 0 and role == Qt.CheckStateRole:
            self._check(index, Qt.CheckState(value))
            self.itemChecked.emit(self.nodeFromIndex(index))
            return True

    def checkMultipleItems(self, index_list, state):
        self.beginResetModel()
        for index in index_list:
            self._check(index, state)
        self.endResetModel()

    def _check(self, index, state):
        item = self.nodeFromIndex(index)
        if state == Qt.Checked:
            if item not in self.checked_list:
                self.checked_list.append(item)
        else:
            if item in self.checked_list:
                self.checked_list.remove(item)
        item.check(state)
        self.dataChanged.emit(index, index)
        if item.childCount():
            for child in item._children:
                child_index = self.index(child.row(), 0, index)
                self._check(child_index, state)

    def nodeFromIndex(self, index):
        if index is not None and index.isValid():
            return index.internalPointer()
        return self._root

    def insertRows(self, position, items, parent=QModelIndex()):
        if parent is None:
            parent = QModelIndex()
        parentItem = self.nodeFromIndex(parent)
        self.beginInsertRows(parent, position, position + len(items) - 1)
        parentItem.insertChildren(position, items)
        self.endInsertRows()
        return True

    def flags(self, index: PySide2.QtCore.QModelIndex) -> PySide2.QtCore.Qt.ItemFlags:
        defaultFlags = super().flags(index)
        if self.CHECKABLE:
            defaultFlags |= Qt.ItemIsUserCheckable
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsSelectable | Qt.ItemIsEnabled | defaultFlags
        else:
            Qt.ItemIsDropEnabled | defaultFlags

    def removeRows(self, row: int, count: int, parent: PySide2.QtCore.QModelIndex = ...) -> bool:
        parent_ = self.nodeFromIndex(parent)
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            parent_.removeChild(row)
        self.endRemoveRows()
        return True

    def removeChild(self, row, _parent):
        self.removeRows(row, 1, _parent)
