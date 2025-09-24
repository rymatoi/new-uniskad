from copy import copy
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import PySide2
from PySide2.QtCore import QAbstractItemModel, QPointF, Signal
from PySide2.QtGui import QIcon, QFont, QColor, QPainter, QPen, QPixmap

from PySide2.QtCore import Qt, QModelIndex

from db import sp
from db.tables import PRODUCT, PROJECT_TABLE


def _save_product_records(records: Sequence[Tuple]):
    for record in records:
        sp.new_update_product_from_record(record)


def _save_project_records(records: Sequence[Tuple]):
    if records:
        sp.new_update_project_from_record_array(records)


SCHEME_SAVE_HANDLERS: Dict[Tuple[str, ...], Callable[[Sequence[Tuple]], None]] = {
    PRODUCT: _save_product_records,
    PROJECT_TABLE: _save_project_records,
}

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
        self.search_highlight = False

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
            if getattr(node, 'search_highlight', False):
                highlight = QColor('#fff59d')
                if node.font_bgcolor:
                    base_color = QColor(node.font_bgcolor)
                    mixed = QColor(
                        (base_color.red() + highlight.red()) // 2,
                        (base_color.green() + highlight.green()) // 2,
                        (base_color.blue() + highlight.blue()) // 2,
                    )
                    return mixed
                return highlight
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

    # --- Drag and drop helpers -------------------------------------------------

    def _node_path(self, node: Node) -> Tuple[int, ...]:
        path: List[int] = []
        current = node
        while current and current is not self._root:
            path.append(current.row())
            current = current.parent()
        return tuple(reversed(path))

    def _prepare_nodes(self, indexes: Sequence[QModelIndex]) -> List[Node]:
        unique: Dict[int, Node] = {}
        for index in indexes:
            if not index.isValid() or index.column() != 0:
                continue
            node = index.internalPointer()
            unique.setdefault(id(node), node)
        nodes = list(unique.values())
        return self._filter_top_nodes(nodes)

    def _filter_top_nodes(self, nodes: Sequence[Node]) -> List[Node]:
        top_level: List[Node] = []
        for node in nodes:
            if not any(self._is_descendant(other, node) for other in nodes if other is not node):
                top_level.append(node)
        return top_level

    def _is_descendant(self, ancestor: Node, candidate: Node) -> bool:
        current = candidate
        while current and current is not self._root:
            if current is ancestor:
                return True
            current = current.parent()
        return False

    def _set_parent_id(self, node: Node, parent: Node) -> None:
        if not getattr(node, '_data', None):
            return
        parent_id = self.root_id if parent is self._root else getattr(parent._data, 'id', self.root_id)
        node._data.set_val('id_up', parent_id)

    def _validate_move(self, nodes: Sequence[Node], target_parent: Node) -> bool:
        if not nodes:
            return False
        parent_node = target_parent or self._root

        for node in nodes:
            if parent_node is node or self._is_descendant(node, parent_node):
                return False

        allowed_types = tuple(parent_node.container_types()) if hasattr(parent_node, 'container_types') else tuple()
        same_parent = all(node.parent() is parent_node for node in nodes)

        if not allowed_types and not same_parent and parent_node is not self._root:
            return False

        if allowed_types:
            for node in nodes:
                if node.parent() is parent_node:
                    continue
                if not isinstance(node, allowed_types):
                    return False

        return True

    def _persist_structure_changes(self, parents: Iterable[Node]) -> None:
        processed: Set[int] = set()
        for parent in parents:
            if parent is None or id(parent) in processed:
                continue
            processed.add(id(parent))

            updates: Dict[Tuple[str, ...], List[Tuple]] = {}
            for position, child in enumerate(parent.children):
                if hasattr(child._data, 'npp'):
                    child._data.npp = position
                scheme = getattr(child, 'scheme', None)
                if scheme and scheme in SCHEME_SAVE_HANDLERS:
                    updates.setdefault(scheme, []).append(child._data.table_fit(scheme))

            for scheme, records in updates.items():
                if records:
                    saver = SCHEME_SAVE_HANDLERS.get(scheme)
                    if saver:
                        saver(records)

    def can_drop_indexes(self, indexes: Sequence[QModelIndex], parent_index: QModelIndex, row: int) -> bool:
        nodes = self._prepare_nodes(indexes)
        target_parent = self.nodeFromIndex(parent_index)
        return self._validate_move(nodes, target_parent)

    def move_indexes(self, indexes: Sequence[QModelIndex], parent_index: QModelIndex, row: Optional[int]) -> Tuple[bool, List[QModelIndex]]:
        nodes = self._prepare_nodes(indexes)
        target_parent = self.nodeFromIndex(parent_index)

        if not self._validate_move(nodes, target_parent):
            return False, []

        move_data = []
        for node in nodes:
            move_data.append({
                'node': node,
                'old_parent': node.parent(),
                'old_row': node.row(),
                'sort_key': self._node_path(node),
            })

        move_data.sort(key=lambda item: item['sort_key'])

        insert_row = row if row is not None else target_parent.childCount()
        insert_row = max(0, insert_row)

        # Adjust insertion point for moves within the same parent
        adjusted_row = insert_row
        for item in move_data:
            if item['old_parent'] is target_parent and item['old_row'] < insert_row:
                adjusted_row -= 1

        self.layoutAboutToBeChanged.emit()

        # Remove nodes from their old parents
        removal_map: Dict[Node, List[Dict[str, object]]] = {}
        for item in move_data:
            parent = item['old_parent']
            removal_map.setdefault(parent, []).append(item)

        for parent, children in removal_map.items():
            for item in sorted(children, key=lambda data: data['old_row'], reverse=True):
                parent.removeChild(item['old_row'])

        current_row = min(adjusted_row, target_parent.childCount())
        for item in move_data:
            target_parent.insertChildren(current_row, [item['node']])
            current_row += 1

        self.layoutChanged.emit()

        # Update parent ids and persist structure
        for item in move_data:
            self._set_parent_id(item['node'], target_parent)

        affected_parents = {item['old_parent'] for item in move_data if item['old_parent']}
        affected_parents.add(target_parent)
        self._persist_structure_changes(affected_parents)

        new_indexes = [self.createIndex(item['node'].row(), 0, item['node']) for item in move_data]
        return True, new_indexes

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
            return Qt.ItemIsDropEnabled | defaultFlags

    def removeRows(self, row: int, count: int, parent: PySide2.QtCore.QModelIndex = ...) -> bool:
        parent_ = self.nodeFromIndex(parent)
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            parent_.removeChild(row)
        self.endRemoveRows()
        return True

    def removeChild(self, row, _parent):
        self.removeRows(row, 1, _parent)
