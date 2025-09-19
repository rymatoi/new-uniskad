import ast
import re
from copy import copy
from datetime import datetime

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, QSortFilterProxyModel, QSize, QLocale, QTimer, QPersistentModelIndex
from PySide2.QtGui import QIcon, QCursor, QColor, QFont, QBrush, QKeySequence
from PySide2.QtWidgets import QTreeView, QMenu, QColorDialog, QInputDialog, QDockWidget, \
    QHBoxLayout, QToolButton, QWidget, QLabel, QAbstractItemView, QAction, QLineEdit, QShortcut, \
    QFontDialog, QComboBox, QCompleter, QTableWidget, QTableWidgetItem, QVBoxLayout, QTreeWidget, QTreeWidgetItem, \
    QApplication, QStyle
from openpyxl.workbook import Workbook
from app import app_logger, _menu, basic_funcs
from app._eval_expr import eval_expr
from app.basic_funcs import timing_decorator
from app.formula import FormulaDelegate
from app.plugins.base_state.models import Node
from db import sp, session

logger = app_logger.get_logger(__name__)


class Tab(QDockWidget):
    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self._parent = parent
        self.index = index
        self.item = index.internalPointer()
        self.setWindowTitle(self.item.data())
        self.ui = None

    def setupUi(self, ui):
        widget = QWidget(self)
        widget.ui = ui
        widget.ui.setupUi(widget)
        self.ui = widget.ui
        self.setWidget(widget)

    def connect_triggered_funcs(self, index):
        pass

    def _connect_func(self, action_name, func):
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(func)

    def create_connections(self):
        pass

    def closeEvent(self, event) -> None:
        del self._parent._opened_tabs[self.index]
        self.close()

    def add_data(self, obj_list):
        pass

    def refresh(self, index):
        index.model().dataChanged.emit(index, index)


class TreeView(QTreeView):
    DISABLE_MENU = False
    DOUBLE_CLICK_OPEN = True
    HIDE_REMOVED_ITEMS = True

    def __init__(self, parent, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.dock_widget = None

        self.setSelectionMode(QTreeView.ExtendedSelection)  # Позволяет выделять несколько элементов
        self.setSelectionBehavior(QTreeView.SelectItems)  # Выделение элементов, а не строк
        # self.setSelectionMode(self.ExtendedSelection)  # разрешаем множественное выделение элементов
        self.setDragDropMode(QAbstractItemView.DragDrop)  # разрешили drag'n'drop
        self.setDragEnabled(True)  # включаем Drag
        self.setAcceptDrops(True)  # включаем Drop
        self.setDropIndicatorShown(True)  # включаем индикатор, указывающий допустимость перемещения элемента
        self.setAnimated(True)

        self.available_actions = []
        self._parent = parent
        self.current_index = None
        self._default_tab = Tab
        self._link_dict = {
            Node: self._default_tab
        }

        self._actions_initialized = []

        self.treeview_menu = []
        # base_menu - стандартный набор пунктов для любого элемента дерева (open+settings)
        self.base_menu = [m for m in self._load_menu(mode='base_state', location='treeview') if m.name != '_icon']
        self.removed_items_menu = self._load_menu('any', 'removed_items')

        self._opened_tabs = {}

        self._search_text = ''
        self._search_results = []
        self._search_expanded_state = None
        self._search_current_index = None
        self._sort_snapshot = None
        self._is_sorted = False
        self._sort_order = None

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__create_connections()
        icon_size = QSize(16, 16)
        self.setIconSize(icon_size)

    def init_dock_widget(self, dock_widget):
        self.dock_widget = dock_widget
        self.dock_widget.init_settings()

    def link_nodes_with_tabs(self, link_dict):
        """Связывает узел и вкладку, которая открывается при выборе узла"""
        self._link_dict = link_dict

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(TreeView, self).setModel(model)
        model.set_view(self)
        self.model().font_name = 'Times New Roman'
        self.model().font_size = 14
        if self.main_window:
            if font_name := self.main_window.user_settings.get('font_name'):
                self.model().font_name = font_name
            if font_size := self.main_window.user_settings.get('font_size'):
                self.model().font_size = font_size
        self.resizeColumnToContents(0)
        self.refresh()
        self._reset_tree_state()

    def _reset_tree_state(self):
        self._search_text = ''
        self._search_results = []
        self._search_expanded_state = None
        self._search_current_index = None
        self._sort_snapshot = None
        self._is_sorted = False
        self._sort_order = None

    def refresh(self):
        for row in range(self.model().rowCount()):
            index = self.model().index(row, 0)
            hidden = self.model().data(index, Qt.UserRole)
            if not self.HIDE_REMOVED_ITEMS:
                self.setItemVisibility(self.model(), index, False)
            else:
                self.setItemVisibility(self.model(), index, hidden)

    def setItemVisibility(self, model, index, hidden):
        self.setRowHidden(index.row(), index.parent(), hidden)
        for i in range(model.rowCount(index)):
            childIndex = model.index(i, 0, index)
            hidden = model.data(childIndex, Qt.UserRole)
            if not self.HIDE_REMOVED_ITEMS:
                self.setItemVisibility(model, childIndex, False)
            else:
                self.setItemVisibility(model, childIndex, hidden)

    def apply_search(self, text):
        model = self.model()
        if model is None:
            return
        normalized = text.strip()
        if not normalized:
            self.clear_search()
            return
        pattern = normalized.casefold()
        if self._search_expanded_state is None:
            self._search_expanded_state = self._capture_expanded_state()
        self._search_text = normalized
        self._search_results = []
        self._search_current_index = None
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            self._apply_search_recursive(index, pattern)
        self._ensure_first_match_visible()

    def clear_search(self):
        model = self.model()
        if model is None:
            return
        if not (self._search_text or self._search_results or self._search_expanded_state):
            return
        self._search_text = ''
        self._search_results = []
        self._search_current_index = None
        self._clear_highlight()
        if self._search_expanded_state is not None:
            self._restore_expanded_state()
        self.viewport().update()

    def has_active_search(self):
        return bool(self._search_text)

    def _ensure_first_match_visible(self):
        if not self._search_results:
            self._search_current_index = None
            return
        selection_model = self.selectionModel()
        if selection_model:
            current_index = selection_model.currentIndex()
            if current_index.isValid():
                persistent_current = QPersistentModelIndex(current_index)
                for idx, persistent in enumerate(self._search_results):
                    if persistent.isValid() and persistent == persistent_current:
                        if self._focus_search_result(idx):
                            return
        self._focus_search_result(0)

    def _focus_search_result(self, start_index):
        if not self._search_results:
            self._search_current_index = None
            return False
        total = len(self._search_results)
        selection_model = self.selectionModel()
        for offset in range(total):
            idx = (start_index + offset) % total
            persistent = self._search_results[idx]
            if not persistent.isValid():
                continue
            index = QtCore.QModelIndex(persistent)
            if selection_model:
                selection_model.setCurrentIndex(
                    index,
                    QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows
                )
            self.scrollTo(index)
            self._search_current_index = idx
            return True
        self._search_current_index = None
        return False

    def next_search_result(self):
        if not self._search_results:
            return
        if self._search_current_index is None:
            start = 0
        else:
            start = (self._search_current_index + 1) % len(self._search_results)
        self._focus_search_result(start)

    def has_search_results(self):
        return any(persistent.isValid() for persistent in self._search_results)

    def _apply_search_recursive(self, index, pattern):
        model = self.model()
        node = index.internalPointer()
        node_text = ''
        if node:
            data = node.data()
            node_text = str(data).casefold() if data is not None else ''
        match = bool(pattern) and pattern in node_text
        child_match = False
        for row in range(model.rowCount(index)):
            child_index = model.index(row, 0, index)
            if self._apply_search_recursive(child_index, pattern):
                child_match = True
        self._set_node_highlight(index, match)
        if match:
            self._search_results.append(QPersistentModelIndex(index))
        if match or child_match:
            self.expand(index)
            return True
        self.collapse(index)
        return False

    def _set_node_highlight(self, index, highlight):
        node = index.internalPointer()
        if not node or getattr(node, 'search_highlight', False) == highlight:
            return
        node.search_highlight = highlight
        self.model().dataChanged.emit(index, index, [Qt.BackgroundRole])

    def _clear_highlight(self):
        model = self.model()
        if model is None:
            return
        for index in self._iter_indexes():
            self._set_node_highlight(index, False)

    def _iter_indexes(self, parent_index=QtCore.QModelIndex()):
        model = self.model()
        if model is None:
            return
        for row in range(model.rowCount(parent_index)):
            index = model.index(row, 0, parent_index)
            yield index
            yield from self._iter_indexes(index)

    def _capture_expanded_state(self):
        expanded = []
        model = self.model()
        if model is None:
            return expanded

        def recurse(parent_index):
            for row in range(model.rowCount(parent_index)):
                index = model.index(row, 0, parent_index)
                if self.isExpanded(index):
                    expanded.append(QPersistentModelIndex(index))
                recurse(index)

        recurse(QtCore.QModelIndex())
        return expanded

    def _restore_expanded_state(self):
        if not self._search_expanded_state:
            self._search_expanded_state = None
            return
        self.collapseAll()
        for persistent in self._search_expanded_state:
            if persistent.isValid():
                self.expand(persistent)
        self._search_expanded_state = None

    def sort_items(self, order=Qt.AscendingOrder):
        model = self.model()
        if model is None:
            return
        if not self._is_sorted:
            self._sort_snapshot = self._capture_sort_snapshot()
        self._is_sorted = True
        self._sort_order = order
        model.layoutAboutToBeChanged.emit()
        self._sort_node(model._root, order == Qt.AscendingOrder)
        model.layoutChanged.emit()
        self.refresh()

    def reset_sort(self):
        model = self.model()
        if model is None or not self._is_sorted or not self._sort_snapshot:
            return
        model.layoutAboutToBeChanged.emit()
        self._restore_sort_snapshot(model._root, self._sort_snapshot)
        model.layoutChanged.emit()
        self._is_sorted = False
        self._sort_order = None
        self._sort_snapshot = None
        self.refresh()

    def has_active_sort(self):
        return self._is_sorted

    def current_sort_order(self):
        return self._sort_order

    def _capture_sort_snapshot(self):
        order = {}
        model = self.model()
        if model is None:
            return order

        def recurse(node):
            children = getattr(node, '_children', [])
            if not children:
                return
            order[id(node)] = [id(child) for child in children]
            for child in children:
                recurse(child)

        recurse(model._root)
        return order

    def _sort_node(self, node, ascending):
        children = getattr(node, '_children', [])
        if not children:
            return

        def sort_key(child):
            name = child.data()
            return (0 if child.is_folder() else 1, str(name).casefold())

        children.sort(key=sort_key, reverse=not ascending)
        for child in children:
            self._sort_node(child, ascending)

    def _restore_sort_snapshot(self, node, snapshot):
        children = getattr(node, '_children', [])
        if not children:
            return
        order_ids = snapshot.get(id(node))
        if order_ids:
            index_map = {child_id: position for position, child_id in enumerate(order_ids)}
            children.sort(key=lambda child: index_map.get(id(child), len(order_ids)))
        for child in children:
            self._restore_sort_snapshot(child, snapshot)

    def get_parent(self, item):
        """Поиск первого элемента типа 'не папка' и возвращение этого элемента."""
        parent = item.parent()
        while parent.is_folder():
            parent = parent.parent()
        return parent

    def get_node_actions(self, item, menu_list):
        '''Обращается к модели и запрашивает массив действий для элемента item из списка menu_list.
        menu_list - все возможные действия для текущего виджета.
        '''
        # если элемент типа папка, то мы не знаем точно, какие могут быть у него дочерние элементы,
        # соответственно, мы не знаем, какой набор internal_actions нам нужен, поэтому мы ищем родительский элемент 'не папка'
        # и запрашиваем internal_actions для родительского элемента, а затем добавляем self_internal_actions.

        if item.is_folder():
            parent = self.get_parent(item)
            return [menu for menu in menu_list if
                    menu.name in list(self.model().action_types[type(parent)]) + list(
                        self.model().self_action_types[type(item)])]
        return [menu for menu in menu_list if
                menu.name in list(self.model().action_types[type(item)]) + list(
                    self.model().self_action_types[type(item)])]

    def get_base_actions(self, item, menu_list):
        return [menu for menu in menu_list if menu.name not in item.exclude_from_base_actions]

    def root_item(self):
        return self.model()._root

    def __create_connections(self):
        """Создание привязок к элементам древовидного интерфейса"""
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.header().sectionClicked.connect(self.selectAll)
        self.doubleClicked.connect(self.open_item)

    def on_context_menu(self, pos):
        if not self.DISABLE_MENU:
            index = self.indexAt(pos)
            menu = self.menu(index)
            menu.exec_(self.viewport().mapToGlobal(pos))

    def _load_menu(self, mode='base_state', location='treeview'):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def menu(self, index):
        menu = QMenu(self)
        # клик по элементу - получаем сам элемент, клик по пустому пространству - получаем корень
        item = index.internalPointer() if index.isValid() else self.root_item()

        if item.has_customization:
            base_menu = self.base_menu
        else:
            base_menu = [m for m in self.base_menu if m.name != '_customize_node']

        if index.isValid():
            if hasattr(item._data, 'deleted') and item._data.deleted is True:
                _menu.init_menu(self.removed_items_menu, self,
                                menu)
            else:
                _menu.init_menu(
                    self.get_base_actions(item, base_menu) + self.get_node_actions(item, self.treeview_menu), self,
                    menu)
        else:
            _menu.init_menu(self.get_node_actions(item, self.treeview_menu), self, menu)
        self.connect_default_triggered_funcs(index)
        self.connect_triggered_funcs(index)
        return menu

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def connect_triggered_funcs(self, index):
        # здесь надо привязать функции к экшенам
        # функции для стаднартных действий ('add', 'remove' ..) привязываются автоматически,
        # функции для обработки этих действий описываются в моделях самих узлов
        pass

    def connect_default_triggered_funcs(self, index):
        item = index.internalPointer() if index.isValid() else self.root_item()

        self._connect_func('_font', self.change_property, 'font', index)
        self._connect_func('_font_color', self.change_property, 'font_text_color', index)
        self._connect_func('_font_bcolor', self.change_property, 'font_bgcolor', index)
        self._connect_func('_icon', self.change_property, 'icon', index)
        self._connect_func('_customize_node', self.customize_node, index)
        self._connect_func('_rename_node', self.change_property, 'name', index)

        self._connect_func('_open', self.open_item, index)
        self._connect_func(f'_remove_{item.internal_type()}', self.remove, index)
        self._connect_func(f'_remove', self.remove, index)

        self._connect_func(f'_final_remove', self.remove, index, True)
        self._connect_func(f'_restore', self.restore, index)

        self._connect_func('_export', self.export_item, index)

        self._connect_func('_move_up', self.move_node, 'up', index)
        self._connect_func('_move_down', self.move_node, 'down', index)
        self._connect_func('_move_top', self.move_node, 'top', index)
        self._connect_func('_move_bottom', self.move_node, 'bottom', index)

        for child in item.container_types():
            type_ = child.internal_type()
            self._connect_func(f'_add_{type_}', self.add_item, type_, index)

    def move_node(self, side, index):
        item = index.internalPointer()
        item_parent = item.parent()
        parent_children = item_parent.children
        item_row = item.row()
        destination_index = None
        hidden_state = None
        if side == 'up':
            row = index.row()
            if row > 0 and index.parent().isValid():
                destination_index = self.model().index(row - 1, index.column(), index.parent())
                hidden_state = self.model().data(destination_index, Qt.UserRole)
                self.model().moveItem(index, destination_index)

        elif side == 'down':
            row = index.row()
            parent_index = index.parent()
            if row < self.model().rowCount(parent_index) - 1 and parent_index.isValid():
                destination_index = self.model().index(row + 1, index.column(), parent_index)
                hidden_state = self.model().data(destination_index, Qt.UserRole)
                self.model().moveItem(index, destination_index)
        if destination_index:
            self.setItemVisibility(self.model(), index, hidden_state)

    def customize_node(self, index):
        item = index.internalPointer()
        customized_nodes = item.customize()
        if not customized_nodes:
            return
        if not isinstance(customized_nodes, tuple):
            customized_nodes = (customized_nodes,)
        self.update_external_nodes(customized_nodes)

    def update_external_nodes(self, nodes):
        index = True
        for node in nodes:
            for _index in self._opened_tabs.keys():
                if node == _index.internalPointer():
                    try:
                        self._opened_tabs[_index].refresh(index)
                    except AttributeError as e:
                        logger.info(f'У элемента {node.data()} нет реализации обновления содержимого вкладки.')

    def get_opened_tabs(self):
        return self._opened_tabs.values()

    def update_tab(self, index):
        pass

    def add_item(self, type_, index):
        parent = index.internalPointer() if index.isValid() else self.root_item()
        logger.info(f'Добавление элемента типа "{type_}".')
        up_node_id = parent._data.id if parent._data else self.model().root_id
        node_type = self.model().item_types.get(type_, 'node')
        item = node_type.add(up_node_id, parent)
        self._add_item(item, index, up_node_id, parent)

    def _add_item(self, item, index, up_node_id, parent):
        if item:
            if isinstance(item, tuple):
                if isinstance(item[0], Node):
                    self.model()._setup_props([item_._data for item_ in item])
                    self.model().custom_ini_tree([item_._data for item_ in item], up_node_id, parent,
                                                 root_item_index=index)
                else:
                    self.model()._setup_props(item)
                    self.model().custom_ini_tree(item, up_node_id, parent,
                                                 root_item_index=index)
                self.model().dataChanged.emit(index, index)
                if self.isExpanded(index):
                    self.setExpanded(index, False)
                    self.setExpanded(index, True)
            else:
                self.insertRow(item, index)
                self.model().dataChanged.emit(index, index)

    def export_item(self, index):
        item = index.internalPointer()
        item.export(item)

    def remove(self, index, final=False):
        if len(self.selectedIndexes()) == 0 and index is not None and index.isValid():
            indexes = [index]
        elif len(self.selectedIndexes()) == 1:
            indexes = [index]
        else:
            indexes = self.selectedIndexes()
        for _index in indexes:
            if _index.isValid():
                item = _index.internalPointer()
                success = item.remove(item, final=final)
                if success:
                    if final:
                        self.removeRow(item.row(), _index.parent())
                    else:
                        if self.HIDE_REMOVED_ITEMS:
                            self.setItemVisibility(self.model(), _index, True)
                    if _index in self._opened_tabs.keys():
                        self._opened_tabs[_index].close()
                else:
                    basic_funcs.error('Ошибка', str(success))

    def restore(self, index):
        # TODO исправить проблему с выделением лишнего
        if len(self.selectedIndexes()) == 1:
            indexes = [index]
        else:
            indexes = self.selectedIndexes()
        for _index in indexes:
            if _index.isValid():
                item = _index.internalPointer()
                success = item.restore(item)
                if success:
                    self.setItemVisibility(self.model(), _index, False)

    def check_availability(self, item, action):
        if f'_{action}' in item.exclude_from_base_actions:
            return False
        return True

    def open_item(self, index):
        if not self.DOUBLE_CLICK_OPEN:
            return

        if self._opened_tabs.get(index, None):
            self._opened_tabs[index].raise_()
            return

        item = index.internalPointer()
        if not self.check_availability(item, 'open'):
            return

        item_type = self.model().item_types.get(item.internal_type(), 'root')
        children = []
        for dock in self._parent.ui.centralWidget.findChildren(QDockWidget):
            children.append(dock)

        tab = self._link_dict.get(item_type, self._default_tab)(index, self, self.main_window)
        self._opened_tabs[index] = tab

        if children:
            self._parent.ui.centralWidget.tabifyDockWidget(children[0], tab)
        else:
            self._parent.ui.centralWidget.addDockWidget(Qt.TopDockWidgetArea, tab)
        tab.show()
        tab.raise_()

    def change_property(self, prop, index):
        need_tab_update = False
        prop_value = None
        item = index.internalPointer()

        if prop == 'font':

            curr_font = QFont()
            curr_font.setBold(True if item.font_bold == 'True' else False)
            curr_font.setUnderline(True if item.font_underline == 'True' else False)
            curr_font.setItalic(True if item.font_italic == 'True' else False)
            if item.font_name:
                curr_font.setFamily(item.font_name)
            else:
                curr_font.setFamily(self.main_window.user_settings.get('font_name'))
            if item.font_size:
                curr_font.setPointSize(int(item.font_size))
            else:
                curr_font.setPointSize(int(self.main_window.user_settings.get('font_size')))
            curr_font.setStrikeOut(True if item.font_strikeout == 'True' else False)

            ok, font = QFontDialog.getFont(curr_font)
            if ok:
                values = {
                    'font_bold': font.bold(),
                    'font_italic': font.italic(),
                    'font_name': font.family(),
                    'font_size': font.pointSize(),
                    'font_strikeout': font.strikeOut(),
                    'font_underline': font.underline(),
                }

                for _prop, _value in values.items():
                    success = item.update(item,
                                          _prop,
                                          str(_value))
                    if success:
                        setattr(item, _prop, success.prop_value)
                        self.model().dataChanged.emit(index, index)
                return


        elif prop == 'font_text_color':
            prop_value = QColorDialog.getColor(item.font_text_color)
            if prop_value.isValid():
                prop_value = prop_value.name()
            else:
                return
        elif prop == 'font_bgcolor':
            prop_value = QColorDialog.getColor(item.font_bgcolor)
            if prop_value.isValid():
                prop_value = prop_value.name()
            else:
                return
        elif prop == 'name':
            prop_value = basic_funcs.get_text('Переименовать элемент', 'Введите новое имя:', '')
            if not prop_value:
                basic_funcs.error('Ошибка!', 'Имя элемента не может быть пустым.')
                return
            need_tab_update = True

        if prop_value is not None:
            success = item.update(item,
                                  prop,
                                  str(prop_value))
            if success:
                setattr(item, prop, success.prop_value)
                self.model().dataChanged.emit(index, index)

                if need_tab_update:
                    if index in self._opened_tabs:
                        self._opened_tabs[index].refresh(index)

    def insertRow(self, item, index):
        if item:
            self.model().addChild(item, index)
        else:
            logger.error('Не удалось добавить элемент в дерево.')

    def insertRows(self, items, index):
        if len(items):
            self.model().insertRows(self.model().rowCount(), items, index)
        else:
            logger.error('Не удалось добавить элементы в дерево.')

    def removeRow(self, row, parent):
        self.model().removeChild(row, parent)

    def removeRows(self, row, count, parent):
        self.model().removeRows(row, count, parent)


class DockWidget(QDockWidget):
    def __init__(self, title, menu_name, plugin_name, parent=None):
        super().__init__(parent)
        self.plugin_name = plugin_name
        self.available_actions = []
        self._parent = parent
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 2, 4, 2)
        main_layout.setSpacing(2)
        self.menu_name = menu_name

        self.title_label = QLabel()
        self.title_label.setText(title)

        self.settings_menu = []

        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText('Поиск...')
        self.search_line.setClearButtonEnabled(True)
        self.search_line.setMinimumWidth(160)
        self.search_line.setMaximumWidth(240)
        self.search_line.setToolTip('Поиск по дереву')

        self.search_next_button = QToolButton()
        self.search_next_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.search_next_button.setAutoRaise(True)
        self.search_next_button.setToolTip('Следующее совпадение')
        self.search_next_button.clicked.connect(self._on_search_next)
        self.search_next_button.setEnabled(False)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(200)
        self.search_line.textChanged.connect(self._on_search_text_changed)
        self.search_line.returnPressed.connect(self._run_search)
        self._search_timer.timeout.connect(self._run_search)

        self._search_shortcut = QShortcut(QKeySequence.Find, self)
        self._search_shortcut.activated.connect(self._focus_search)

        self.dock_button = QToolButton()
        self.dock_button.setIcon(QIcon(':/dock.png'))
        self.dock_button.setText('Вернуть на окно')
        self.dock_button.clicked.connect(self.dock_)
        self.dock_button.hide()

        self.sort_button = QToolButton()
        self.sort_button.setIcon(QIcon(':/sorting.png'))
        self.sort_button.setToolTip('Сортировка')
        self.sort_button.setPopupMode(QToolButton.InstantPopup)
        self.sort_button.setAutoRaise(True)

        self.sort_menu = QMenu(self)
        self.sort_by_asc_action = self.sort_menu.addAction('По имени (А→Я)')
        self.sort_by_desc_action = self.sort_menu.addAction('По имени (Я→А)')
        self.sort_menu.addSeparator()
        self.sort_reset_action = self.sort_menu.addAction('Без сортировки')
        self.sort_button.setMenu(self.sort_menu)
        self.sort_by_asc_action.triggered.connect(lambda: self._sort_tree(Qt.AscendingOrder))
        self.sort_by_desc_action.triggered.connect(lambda: self._sort_tree(Qt.DescendingOrder))
        self.sort_reset_action.triggered.connect(self._reset_sort)
        self.sort_reset_action.setEnabled(False)

        settings_button = QToolButton()
        settings_button.setIcon(QIcon(':/settings.png'))
        settings_button.setText('Настройки')
        settings_button.clicked.connect(self.show_settings_menu)

        save_button = QToolButton()
        save_button.setIcon(QIcon(':/diskette.png'))
        save_button.setText('Сохранить')
        save_button.clicked.connect(self.save_state)

        up_button = QToolButton()
        up_button.setIcon(QIcon(':/up.png'))
        up_button.setText('Переместить вверх')
        up_button.clicked.connect(self.move_up)

        down_button = QToolButton()
        down_button.setIcon(QIcon(':/down.png'))
        down_button.setText('Переместить вниз')
        down_button.clicked.connect(self.move_down)

        hide_button = QToolButton()
        hide_button.setIcon(QIcon(':/hide.png'))
        hide_button.setText('Закрыть')
        hide_button.clicked.connect(self.hide_)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(save_button)
        header_layout.addWidget(up_button)
        header_layout.addWidget(down_button)
        header_layout.addWidget(self.dock_button)
        header_layout.addWidget(settings_button)
        header_layout.addWidget(hide_button)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(2)
        controls_layout.addStretch()
        controls_layout.addWidget(self.search_line)
        controls_layout.addWidget(self.search_next_button)
        controls_layout.addWidget(self.sort_button)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(controls_layout)

        widget = QWidget()
        widget.setLayout(main_layout)

        objectName = widget.objectName() if widget.objectName() != "" else str(id(widget))
        widget.setObjectName(objectName)
        widget.setStyleSheet("#%s {%s}" % (objectName, 'border: 1px solid grey;'))

        self.setTitleBarWidget(widget)
        self.topLevelChanged.connect(lambda: self.dock_button.setHidden(not self.isFloating()))
        self._update_sort_actions()
        self._update_search_controls()

    def setWidget(self, widget):
        super().setWidget(widget)
        self._on_tree_changed(widget)

    def _tree(self):
        widget = self.widget()
        if isinstance(widget, TreeView):
            return widget
        return None

    def _on_tree_changed(self, widget):
        if isinstance(widget, TreeView):
            if self.search_line.text().strip():
                widget.apply_search(self.search_line.text())
            else:
                widget.clear_search()
        self._update_sort_actions()
        self._update_search_controls()

    def _on_search_text_changed(self, text):
        if text.strip():
            self._search_timer.start(200)
            self.search_next_button.setEnabled(False)
        else:
            self._search_timer.stop()
            self._run_search()
        if not text.strip():
            self._update_search_controls()

    def _run_search(self):
        tree = self._tree()
        if not tree:
            return
        text = self.search_line.text()
        if text.strip():
            tree.apply_search(text)
        else:
            tree.clear_search()
        self._update_search_controls()

    def _sort_tree(self, order):
        tree = self._tree()
        if not tree:
            return
        tree.sort_items(order)
        self._update_sort_actions()
        if self.search_line.text().strip():
            tree.apply_search(self.search_line.text())
        self._update_search_controls()

    def _reset_sort(self):
        tree = self._tree()
        if not tree:
            return
        tree.reset_sort()
        self._update_sort_actions()
        if self.search_line.text().strip():
            tree.apply_search(self.search_line.text())
        self._update_search_controls()

    def _focus_search(self):
        self.search_line.setFocus()
        self.search_line.selectAll()

    def _on_search_next(self):
        tree = self._tree()
        if not tree:
            return
        tree.next_search_result()

    def _update_sort_actions(self):
        has_sort = False
        tree = self._tree()
        if tree:
            has_sort = tree.has_active_sort()
        self.sort_reset_action.setEnabled(has_sort)

    def _update_search_controls(self):
        tree = self._tree()
        has_tree = tree is not None
        text = self.search_line.text().strip()
        has_results = bool(has_tree and text and tree.has_search_results())
        self.search_next_button.setEnabled(has_results)
        self.sort_button.setEnabled(has_tree)

    def update_npps(self, root):
        update_data = []
        for child in root.children:
            child._data.npp = child.row()
            update_data.append(child._data.table_fit(child.scheme))
            update_data += self.update_npps(child)
        return update_data

    def save_state(self):
        pass

    def move_up(self):
        tree = self.widget()
        index = tree.selectionModel().currentIndex()
        if not index.isValid() or index.row() <= 0:
            return

        next_non_deleted_item = None
        if not tree.HIDE_REMOVED_ITEMS:
            next_non_deleted_item = index.parent().child(index.row() - 1, 0)
        else:
            for i in range(index.row() - 1, -1, -1):
                next_item = index.parent().child(i, 0)
                if next_item.isValid():
                    if not next_item.internalPointer()._data.deleted:
                        next_non_deleted_item = next_item
                        break

        if next_non_deleted_item and next_non_deleted_item.isValid():
            tree.model().moveItem(index, next_non_deleted_item)
            if tree.HIDE_REMOVED_ITEMS:
                self.hide_hidden_children(tree, tree.model(), index.parent())

    def move_down(self):
        tree = self.widget()
        index = tree.selectionModel().currentIndex()
        if not index.isValid() or index.row() >= tree.model().rowCount(index.parent()):
            return

        next_non_deleted_item = None
        if not tree.HIDE_REMOVED_ITEMS:
            next_non_deleted_item = index.parent().child(index.row() + 1, 0)
        else:
            for i in range(index.row() + 1, tree.model().rowCount(index.parent()), 1):
                next_item = index.parent().child(i, 0)
                if next_item.isValid():
                    if not next_item.internalPointer()._data.deleted:
                        next_non_deleted_item = next_item
                        break

        if next_non_deleted_item:
            tree.model().moveItem(index, next_non_deleted_item)
            if tree.HIDE_REMOVED_ITEMS:
                self.hide_hidden_children(tree, tree.model(), index.parent())

    def hide_hidden_children(self, tree, model, parent):
        if not parent.isValid():
            return
        for i in range(model.rowCount(parent)):
            child = parent.child(i, 0)
            if child.isValid():
                tree.setItemVisibility(tree.model(), child, child.internalPointer()._data.deleted)

    def init_menu(self):
        self.settings_menu = self._load_menu('any', 'settings_tool_button')

    def set_title_label(self, value):
        self.title_label.setText(value)

    def show_settings_menu(self, pos):
        menu = QMenu(self)
        _menu.init_menu(self.settings_menu, self, menu)
        self.connect_triggered_funcs()
        menu.popup(QCursor.pos())

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def _connect_func(self, action_name, func):
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(func)

    def connect_triggered_funcs(self, index=None):
        # self._connect_func('_structure_control', lambda: self._update_structure_control())
        self._connect_func('_show_removed', lambda: self._show_removed_items())

    def init_settings(self):
        self._show_removed_items()

    def _show_removed_items(self):
        if hasattr(self, '_show_removed'):
            setattr(self.widget(), 'HIDE_REMOVED_ITEMS', not getattr(self, '_show_removed').isChecked())
            self.widget().refresh()

    def hide_(self):
        getattr(self._parent, self.menu_name).setChecked(False)
        self.hide()

    def dock_(self):
        self.setFloating(False)

    def refresh(self):
        pass
        # getattr(self.parent(), self.plugin_name).deactivate()
        # getattr(self.parent(), self.plugin_name).activate()


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


class TableItem(QTableWidgetItem):
    def __init__(self, cell, key):
        super().__init__()
        self.cell = cell
        self.key = key
        self.dependencies = []
        self.cells_in_formula = []

        self.dep_inited = False

    def init_dependencies(self):
        self.dependencies = []
        if dep := self.get('dependencies', ast.literal_eval, None):
            for d in dep:
                cell_key = (d[0], datetime.strptime(d[1], "%Y-%m-%d %H:%M:%S.%f"))
                if cell_key in self.tableWidget().table.keys():
                    self.dependencies.append(cell_key)

    def has_dependencies(self):
        return len(self.dependencies) > 0

    def init_cells_in_formula(self):
        self.cells_in_formula = []
        if dep := self.get('cells_in_formula', ast.literal_eval, None):
            for d in dep:
                cell_key = (d[0], datetime.strptime(d[1], "%Y-%m-%d %H:%M:%S.%f"))
                if cell_key in self.tableWidget().table.keys():
                    self.cells_in_formula.append(cell_key)

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def toString(self, value, precision):
        curr_locale = QLocale()
        val = curr_locale.toString(value, 'f', precision)
        return val

    def value(self):
        tw = self.tableWidget()
        accuracy = tw.get_row_prop(self.key[0], 'accuracy', int, 2)
        plus_val = tw.get_row_prop(self.key[0], 'plus_value', float, 0)
        mul_val = tw.get_row_prop(self.key[0], 'mul_value', float, 1)

        if cformula := self.get('cformula', str):
            try:
                if plus_val:
                    return self.toString(float(cformula) + plus_val, accuracy)
                else:
                    return self.toString(float(cformula) * mul_val, accuracy)
            except:
                return cformula
        if not self.is_float(self.get('value')):
            return self.get('value')

        if plus_val:
            return self.toString(self.get('value', float, 0) + plus_val, accuracy)
        else:
            return self.toString(self.get('value', float, 0) * mul_val, accuracy)

    def data(self, role: int):
        tw = self.tableWidget()

        if role == Qt.DisplayRole:

            if not self.dep_inited:
                self.init_dependencies()
                self.init_cells_in_formula()
                self.dep_inited = True

            return self.value()

        if role == Qt.EditRole:
            return self.get('formula', str, '')

        if role == Qt.BackgroundColorRole:
            if self.get('broken', bool, False):
                return QBrush(Qt.lightGray)
            else:
                if bg_color := self.get('font_bgcolor', str, None):
                    return QColor(bg_color)

        if role == Qt.TextColorRole:
            return QColor(self.get('font_text_color', str))

        if role == Qt.FontRole:
            font = QFont()
            # font.setFamily(self.get('font_name', 'Times'))
            font.setBold(self.get('font_bold', bool, False))
            font.setItalic(self.get('font_italic', bool, False))
            font.setPixelSize(self.get('font_size', int, 14))
            return font

        if role == Qt.TextAlignmentRole:
            return tw.get_column_prop(self.key[1], 'alignment', int, 4)

        return super().data(role)

    def setData(self, role: int, value) -> None:
        if role == Qt.EditRole:
            if isinstance(value, str):
                if value != self.get('formula', str, '='):
                    if value == '':
                        return
                    self.update_cell('formula', value)
                    self.calculate_formula()
                    self.update_dependencies()

    def update_dependencies(self):
        for cell_key in self.dependencies:
            if cell_key in self.tableWidget().table.keys():
                tw = self.tableWidget()
                row = tw.ord_rows.index(cell_key[0])
                column = tw.ord_columns.index(cell_key[1])
                cell = tw.item(row, column)
                cell.calculate_formula()
                cell.update_dependencies()

    def calculate_formula(self):
        formula = self.get('formula', str, '')
        used_cells = []
        for m in re.findall(r'"(?:[^\\"]|\\.)*"', formula):
            param_index = m[1:-1]
            if '[' not in param_index and ']' not in param_index:
                param = param_index.replace('\\', '')
                index = str(self.column() + 1)
            else:
                param_index = param_index.split('[', 1)
                if len(param_index) != 2:
                    self.update_cell('cformula', 'Неверный синтаксис')
                param = param_index[0].replace('\\', '')
                index = param_index[1][:-1]
            if index and index.isdigit():
                tw = self.tableWidget()
                if len(tw.ord_columns) + 1 < int(index) or int(index) < 0:
                    self.update_cell('cformula', 'Неверный индекс')
                column = tw.ord_columns[int(index) - 1]

                if (param, column) not in tw.table.keys():
                    return self.update_cell('cformula', 'Параметр отсутствует в таблице')
                cell = tw.item(tw.ord_rows.index(param), int(index) - 1)
                if cell is None:
                    continue
                used_cells.append(cell)
                if self.key not in cell.dependencies:
                    cell.dependencies.append(self.key)
                    cell.update_cell('dependencies',
                                     str([(_c[0], _c[1].strftime("%Y-%m-%d %H:%M:%S.%f")) for _c in
                                          cell.dependencies]))
                if cell not in self.cells_in_formula:
                    self.cells_in_formula.append(cell.key)

                plus_val = tw.get_row_prop(cell.key[0], 'plus_value', float, 0)
                mul_val = tw.get_row_prop(cell.key[0], 'mul_value', float, 1)
                if cashed_val := cell.get('cformula', float, 0):
                    if plus_val:
                        formula = formula.replace(m, str(cashed_val + plus_val))
                    else:
                        formula = formula.replace(m, str(cashed_val * mul_val))
                else:
                    if plus_val:
                        formula = formula.replace(m, str(cell.get('value', float, 0) + plus_val))
                    else:
                        formula = formula.replace(m, str(cell.get('value', float, 0) * mul_val))
        formula = formula.replace('=', '')
        if formula.replace(' ', '') == '':
            self.update_cell('cformula', '')
            return None
        evaled = str(eval_expr(formula.replace('=', '')))
        if evaled:
            self.update_cell('cformula', evaled)
        self.update_cell('cells_in_formula',
                         str([(_c[0], _c[1].strftime("%Y-%m-%d %H:%M:%S.%f")) for _c in
                              self.cells_in_formula]))
        self.clear_unused_dependencies(used_cells)
        return evaled

    def clear_unused_dependencies(self, used_cells):
        for cell_key in self.cells_in_formula:
            if cell_key in self.tableWidget().table.keys():
                tw = self.tableWidget()
                row = tw.ord_rows.index(cell_key[0])
                column = tw.ord_columns.index(cell_key[1])
                cell = tw.item(row, column)
            else:
                continue
            if cell not in used_cells:
                if self in cell.dependencies:
                    cell.dependencies.remove(self)
                    cell.update_cell('dependencies', str([(_c[0], _c[1].strftime("%Y-%m-%d %H:%M:%S.%f")) for _c in
                                                          cell.dependencies]))

    def get(self, prop, cast_type=None, default=None):
        if prop not in self.cell:
            return default if default is not None else None
        if self.cell[prop].prop_value:
            if cast_type:
                val = self.cell[prop].prop_value
                if cast_type is bool:
                    if isinstance(val, bool):
                        return val
                    else:
                        return True if self.cell[prop].prop_value.lower() == 'true' else False
                else:
                    return self.cast_type(cast_type, prop, default)
            return self.cell[prop].prop_value
        else:
            return default

    def cast_type(self, ct, prop, default):
        if ct is bool:
            if str(self.cell[prop].prop_value).lower() == 'true':
                return True
            elif str(self.cell[prop].prop_value).lower() == 'false':
                return False
            else:
                return default
        else:
            try:
                return ct(self.cell[prop].prop_value)
            except:
                return default

    def update_cell(self, prop, value):
        pass

    def get_prop_template(self, prop_name, prop_value):
        if self.get(prop_name):
            cell = copy(self.cell[prop_name])
            cell.prop_value = prop_value
        else:
            cell = copy(self.cell['value'])
            cell.id_record = None
            cell.param_prop_name = prop_name
            cell.prop_name = prop_name
            cell.prop_value = prop_value
        return cell

    def add_prop(self, obj):
        if hasattr(obj, 'prop_name'):
            self.cell[obj.prop_name] = obj

    def update_prop(self, prop, value):
        self.cell[prop].prop_value = value


class TablePage1(QtWidgets.QWidget):
    TABLE = None

    def __init__(self, cells, item, parent, main_window):
        super().__init__()
        curr_locale = QLocale()

        self.item = item
        self._parent = parent
        self.mw = main_window

        self.edit_cell = None
        self.table = TableWidget(self, main_window) if self.TABLE is None else self.TABLE(self, main_window)

        self.available_actions = []
        self.cell_menu = self._load_menu('any', 'table_cell')
        self.row_menu = self._load_menu('any', 'table_row')
        self.column_menu = self._load_menu('any', 'table_column')
        self.table_menu = self._load_menu('any', 'table')
        self.centralLayout = QVBoxLayout(self)
        self.centralLayout.addWidget(self.table)
        self.setLayout(self.centralLayout)
        self.toolbar = QtWidgets.QToolBar(self)
        self.init_toolbar()
        self.init_table(cells)

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def init_table(self, cells):
        self.table.load_table(cells)
        if hasattr(self.item, 'filters') and self.item.filters and (
                self.item.use_filters == 'True' or self.item.use_filters is True):
            self.table.apply_filters(self.item.filters)
        delegate = FormulaDelegate(parent=self)
        self.table.setItemDelegate(delegate)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_cell_menu)

        row_headers = self.table.verticalHeader()
        row_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        row_headers.customContextMenuRequested.connect(self.show_row_menu)

        column_headers = self.table.horizontalHeader()
        column_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        column_headers.customContextMenuRequested.connect(self.show_column_menu)

    def show_row_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.row_menu, self, menu, _exclude=['_rename_row', '_recalculate_eizm'])
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def show_column_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.column_menu, self, menu)
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def show_cell_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.cell_menu, self, menu)
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def connect_triggered_funcs(self, index):
        self._connect_func('_add_row', self.add_row, index)
        self._connect_func('_add_column', self.add_column, index)
        self._connect_func('_remove_row', self.remove_rows, index)
        self._connect_func('_remove_column', self.remove_columns, index)
        self._connect_func('_rename_row', self.rename_row, index)
        self._connect_func('_row_settings', self.row_settings, index)
        self._connect_func('_column_settings', self.column_settings, index)

    def column_settings(self, index):
        pass

    def remove_columns(self, index):
        for _index in reversed(self.table.selectedIndexes()):
            if _index.column() == index.column():
                continue
            if _index.isValid() and _index.row() == 0:
                self.remove_column(_index)

        self.remove_column(index)

    def remove_rows(self, index):
        for _index in reversed(self.table.selectedIndexes()):
            if _index.row() == index.row():
                continue
            if _index.isValid() and _index.column() == 0:
                self.remove_row(_index)

        self.remove_row(index)

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def show_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.cell_menu, self, menu)
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def init_toolbar(self):
        self.saveAction = QAction(QIcon(":diskette.png"), 'Сохранить изменения', self,
                                  triggered=lambda: self.table.update_table())
        self.boldAction = QAction(QIcon(":bold.png"), 'Жирный шрифт', self,
                                  triggered=lambda: self.change_property('font_bold'))
        self.italicAction = QAction(QIcon(":italic.png"), 'Курсив', self,
                                    triggered=lambda: self.change_property('font_italic'))
        self.sizeAction = QAction(QIcon(":font_size.png"), 'Размер шрифта', self,
                                  triggered=lambda: self.change_property('font_size'))
        self.textColorAction = QAction(QIcon(":font_text_color.png"), 'Цвет текста', self,
                                       triggered=lambda: self.change_property('font_text_color'))
        self.bgcolorAction = QAction(QIcon(":bgcolor.png"), 'Цвет фона', self,
                                     triggered=lambda: self.change_property('font_bgcolor'))

        self.toolbar.addAction(self.saveAction)

        if '_bold_action' in self.available_actions:
            self.toolbar.addAction(self.boldAction)

        if '_italic_action' in self.available_actions:
            self.toolbar.addAction(self.italicAction)

        if '_font_size' in self.available_actions:
            self.toolbar.addAction(self.sizeAction)

        if '_font_text_color' in self.available_actions:
            self.toolbar.addAction(self.textColorAction)

        if '_bgcolor' in self.available_actions:
            self.toolbar.addAction(self.bgcolorAction)

        if '_broken' in self.available_actions:
            self.brokenAction = QAction(QIcon(":broken.png"), 'Битая точка', self,
                                        triggered=lambda: self.change_property('broken'))
            self.toolbar.addAction(self.brokenAction)

        self.toolbar.setIconSize(QtCore.QSize(18, 18))
        self.centralLayout.setMenuBar(self.toolbar)

    def add_toolbar_action(self, action_name, action, toggled=None):
        if action_name in self.available_actions:
            setattr(self, action_name, action)
            self.toolbar.addAction(getattr(self, action_name))
            if toggled is not None:
                getattr(self, action_name).toggled.connect(toggled)
                getattr(self, action_name).setCheckable(True)

    def change_property(self, prop):
        selected_cells = self.table.selectedIndexes()
        if not len(selected_cells):
            return
        first_cell = self.table.itemFromIndex(selected_cells[0])
        result_prop_value = None
        if prop == 'font_text_color':
            result_prop_value = QColorDialog.getColor()
            if not result_prop_value.isValid():
                return
            else:
                result_prop_value = result_prop_value.name()
        elif prop == 'font_bgcolor':
            result_prop_value = QColorDialog.getColor()
            if not result_prop_value.isValid():
                return
            else:
                result_prop_value = result_prop_value.name()
        elif prop == 'font_size':
            result_prop_value = QInputDialog.getInt(self, "Change font size", "Size:", 11, 0,
                                                    100, 1)
            if result_prop_value[1]:
                result_prop_value = result_prop_value[0]
            else:
                return
        if result_prop_value is None:
            result_prop_value = not first_cell.get(prop, bool, False)

        if result_prop_value is None:
            return

        for cell in selected_cells:
            c = self.table.itemFromIndex(cell)
            c.update_cell(prop, str(result_prop_value))

    def bulk_update_cells(self, cells, prop_name, prop_value):
        pass

    def add_row(self, index):
        pass

    def add_column(self, index):
        pass

    def remove_row(self, index):
        pass

    def remove_column(self, index):
        pass

    def rename_row(self, index):
        pass

    def row_settings(self, index):
        pass


class TableWidget(QTableWidget):
    TABLE_ITEM = None

    def __init__(self, parent, main_window):
        super().__init__()
        self.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.columns = {}
        self.ord_columns = []
        self.rows = {}
        self.ord_rows = []
        self.header_names = []
        self.table = {}
        self._parent = parent
        self.mw = main_window

        self.search_string = None
        self.need_update = []

        if self.TABLE_ITEM is None:
            self.TABLE_ITEM = TableItem

        self.create_connections()

    def get_update_cells(self):
        pass

    def update_table(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            search_string, ok = QInputDialog.getText(self, "Поиск", "Введите строку для поиска:")
            if ok:
                self.search_string = search_string
                self.filter_table()
        elif event == QKeySequence.Copy:  # Проверяем, нажата ли комбинация Ctrl+C
            self.copy_to_clipboard()
        else:
            super().keyPressEvent(event)

    def copy_to_clipboard(self):
        """Копируем выделенные ячейки в буфер обмена."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        copied_data = ""
        for range_ in selected_ranges:
            for row in range(range_.topRow(), range_.bottomRow() + 1):
                row_data = [self.ord_rows[row]]
                for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                copied_data += "\t".join(row_data) + "\n"

        # Сохраняем в буфер обмена
        clipboard = QApplication.clipboard()
        clipboard.setText(copied_data.strip())

    def filter_table(self):
        search_string = self.search_string.lower()
        for row in range(self.rowCount()):
            if search_string in self.ord_rows[row].lower():
                self.setRowHidden(row, False)
            else:
                self.setRowHidden(row, True)

    def load_table(self, db_objects):
        self.clear()
        self.table = {}
        self.rows = {}
        self.columns = {}

        list(map(lambda obj: self.get_object(obj).update({obj.prop_name: obj}), db_objects))

        self.setColumnCount(len(self.columns))
        self.setRowCount(len(self.rows))

        self.ord_columns = [column[1] for column in
                            sorted(self.columns.keys(), key=lambda column: self.get_column_npp(column))]
        self.ord_rows = [row[0] for row in
                         sorted(self.rows.keys(), key=lambda row: self.get_row_npp(row))]

        for row in self.rows:
            for column in self.columns:
                cell = self.table[row[0], column[1]]
                item = self.TABLE_ITEM(cell, (row[0], column[1]))
                self.setItem(self.ord_rows.index(row[0]), self.ord_columns.index(column[1]), item)

        self.set_vertical_headers()

        if sp.get_session_role_secret_grantness() is False:
            self.hide_secret_rows()

    def hide_secret_rows(self):
        for row in range(self.rowCount()):
            if self.get_row_prop(self.ord_rows[row], 'is_secret', bool, False):
                self.setRowHidden(row, True)
            else:
                self.setRowHidden(row, False)

    def is_value_broken(self, i, x_value, y_value, condition, condition_percent):
        def is_float(num):
            try:
                float(num)
                return True
            except ValueError:
                return False

        x_row_num = self.ord_rows.index(x_value)
        y_row_num = self.ord_rows.index(y_value)
        x_item = self.item(x_row_num, i)
        y_item = self.item(y_row_num, i)

        if not is_float(y_item.value()) or not is_float(x_item.value()):
            return False

        x_value = float(x_item.value())
        y_value = float(y_item.value())
        condition_percent = float(condition_percent)

        if condition == '>':
            if x_value > y_value * (1 + condition_percent / 100):
                return True
        elif condition == '<':
            if x_value < y_value * (1 - condition_percent / 100):
                return True
        elif condition == '=':
            if x_value == condition_percent:
                return True

        return False

    def apply_filters(self, filters):
        filters = ast.literal_eval(filters)
        for i, column in enumerate(self.ord_columns):
            for filter in filters:
                row_num = self.ord_rows.index(filter['x'])
                cell_item = self.item(row_num, i)
                if self.is_value_broken(i, filter['x'], filter['y'], filter['condition'], filter['condition_percent']):
                    cell_item.update_cell('broken', 'True')
                else:
                    cell_item.update_cell('broken', 'False')

    def set_vertical_headers(self):
        self.setVerticalHeaderLabels(self.ord_rows)

    def convert_to_float(self, val):
        try:
            return float(val)
        except ValueError:
            return str(val)

    def export(self, filename):
        wb = Workbook()
        ws = wb.active
        for i, row in enumerate(self.ord_rows):
            ws.cell(i + 1, 1).value = row
            for j, col in enumerate(self.ord_columns):
                cell = self.item(i, j)
                ws.cell(i + 1, j + 2).value = self.convert_to_float(
                    cell.get('cformula', str, cell.get('value', str, '')))
        wb.save(filename)

    def update_ord_row(self, new_name, old_name):
        row_num = self.ord_rows.index(old_name)
        self.ord_rows[row_num] = new_name
        self.setVerticalHeaderLabels(self.ord_rows)

        for i, c in enumerate(self.ord_columns):
            if (old_name, None) in self.rows:
                row = self.rows[old_name, None]
                self.rows[new_name, None] = row
                del self.rows[old_name, None]
            cell = self.table[old_name, c]
            cell_item = self.item(row_num, i)
            self.table[new_name, c] = cell
            for prop in cell:
                cell[prop].excel_param_name = new_name
            for prop in cell_item.cell:
                cell_item.cell[prop].excel_param_name = new_name
            del self.table[old_name, c]

        for cell in self.need_update:
            if cell.excel_param_name == old_name:
                cell.excel_param_name = new_name

    def add_row(self, db_objects):
        if not len(db_objects):
            return
        new_row = db_objects[0].excel_param_name

        list(map(lambda obj: self.get_object(obj).update({obj.prop_name: obj}), db_objects))

        self.ord_rows.append(new_row)
        self.setRowCount(len(self.ord_rows))

        for column in self.columns:
            cell = self.table[new_row, column[1]]
            item = self.TABLE_ITEM(cell, (new_row, column[1]))
            self.setItem(self.ord_rows.index(new_row), self.ord_columns.index(column[1]), item)
            if item.get('formula', str, None):
                item.calculate_formula()

        self.setVerticalHeaderLabels(self.ord_rows)

        # for i, row in enumerate(self.ord_rows):
        #     self.setVerticalHeaderItem(i, HeaderItem(row, self.rows[row, None]))

    def add_column(self, db_objects):
        if not len(db_objects):
            return
        new_column = db_objects[0].date_time_izm
        list(map(lambda obj: self.get_object(obj).update({obj.prop_name: obj}), db_objects))

        self.ord_columns.append(new_column)
        self.setColumnCount(len(self.ord_columns))

        for row in self.rows:
            cell = self.table[row[0], new_column]
            item = self.TABLE_ITEM(cell, (row[0], new_column))
            self.setItem(self.ord_rows.index(row[0]), self.ord_columns.index(new_column), item)

    def create_connections(self):
        pass

    def get_object(self, obj):
        param_name = getattr(obj, 'excel_param_name') if getattr(obj, 'sprav_name') is None else getattr(obj,
                                                                                                         'sprav_name')
        if obj.date_time_izm is None:
            if (param_name, obj.date_time_izm) not in self.rows:
                self.rows[(param_name, obj.date_time_izm)] = {}
            return self.rows[(param_name, obj.date_time_izm)]
        elif param_name is None:
            if (param_name, obj.date_time_izm) not in self.columns:
                self.columns[(param_name, obj.date_time_izm)] = {}
            return self.columns[(param_name, obj.date_time_izm)]
        else:
            if (param_name, obj.date_time_izm) not in self.table:
                self.table[(param_name, obj.date_time_izm)] = {}
            return self.table[(param_name, obj.date_time_izm)]

    def get_row_npp(self, row):
        return self.get_row_prop(row, 'row_npp', int, None)

    def get_row_prop(self, row, prop_name, type_, default=None):
        if isinstance(row, tuple) and len(row) == 2 and row[1] is None:
            if prop_name in self.rows[row]:
                return type_(self.rows[row][prop_name].prop_value)
            else:
                return default
        elif isinstance(row, str) and (row, None) in self.rows.keys():
            if prop_name in self.rows[(row, None)]:
                return type_(self.rows[(row, None)][prop_name].prop_value)
            else:
                return type_(default)
        else:
            return type_(default)

    def get_column_prop(self, column, prop_name, type_, default=None):
        if isinstance(column, tuple) and len(column) == 2 and column[0] is None:
            if prop_name in self.columns[column]:
                return type_(self.columns[column][prop_name].prop_value)
            else:
                return default
        elif (None, column) in self.columns.keys():
            if prop_name in self.columns[(None, column)]:
                return type_(self.columns[(None, column)][prop_name].prop_value)
            else:
                return type_(default)
        else:
            return type_(default)

    def get_column_npp(self, column):
        return int(self.columns[column]['column_npp'].prop_value)

    def update_row_obj(self, row, prop_name, obj):
        if isinstance(row, tuple) and len(row) == 2 and row[1] is None:
            self.rows[row][prop_name] = obj
        elif isinstance(row, str) and (row, None) in self.rows.keys():
            self.rows[(row, None)][prop_name] = obj

    def update_column_obj(self, column, prop_name, obj):
        if isinstance(column, tuple) and len(column) == 2 and column[0] is None:
            self.columns[column][prop_name] = obj
        elif (None, column) in self.columns.keys():
            self.columns[(None, column)][prop_name] = obj
