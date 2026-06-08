import ast
from copy import copy, deepcopy
from datetime import datetime

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection
from PySide6.QtGui import QBrush, QColor, QIcon, QAction
from PySide6.QtWidgets import QTreeWidgetItem, QMessageBox, QToolButton, QMenu

from app.plugins.project.dialogs.select_user import UserSelectionDialog
from app.plugins.project.models import ProjectTreeModel, ProjectNode
from db import sp
from db.tables import PROJECT_TABLE
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_select_project_dialog import Ui_SelectProjectDialog


class ProjectSelectionDialog(BaseDialog):

    def __init__(self, auto_open_id=None, main_window=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        dc = main_window.data_cache

        self.ui = Ui_SelectProjectDialog()
        self.ui.setupUi(self)

        self.main_window = main_window

        self.icons = {
            4: ':/project_copy.png',
            20: ':/project.png',
            5: ':/test.png',
            6: ':/folder.png',
            8: ':/graph.png',
            11: ':/epure.png',
            12: ':/assembly.png',
            13: ':/model.png',
            14: ':/product.png',
            15: ':/folder.png',
            17: ':/folder.png',
            18: ':/folder.png',
            19: ':/file.png',
        }

        self.users = {user.id: f'{user.name} {user.fam}' for user in sp.get_full_users_list() if not user.deleted}

        self.project_types = dc.get_project_types(reversed=True)
        self.projects = []
        for project in sp.get_user_projects():
            project.type_ = self.project_types[project.project_type]
            self.projects.append(project)

        self.search_box.setPlaceholderText("Поиск по имени")

        # self.sort_by_date_button.clicked.connect(self.toggle_search_mode)
        self.search_box.textChanged.connect(self.search_projects)

        # Установить количество столбцов
        self.personal_tree.setColumnCount(2)
        self.shared_tree.setColumnCount(2)

        # Установить заголовки столбцов
        self.personal_tree.setHeaderLabels(["Имя", "Последнее изменение"])
        self.shared_tree.setHeaderLabels(["Имя", "Последнее изменение"])
        self.project_props = {}
        self.build_tree()
        self.ui.copyButton.setEnabled(False)
        self.ui.renameButton.setEnabled(False)
        self.ui.selectButton.setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        self.ui.passProjectButton.setEnabled(False)
        self.ui.removeButton.setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Подгоняем колонки под контент
        self.setWindowTitle('Мои проекты')
        self.search_mode = 'name'
        self.create_connections()  # создаем привязки
        self.auto_open_id = auto_open_id
        self.personal_tree.resizeColumnToContents(0)
        self.shared_tree.resizeColumnToContents(0)

        self.sort_by_date_button.hide()
        # Создаем новую кнопку сортировки
        self.create_sort_button()

        self.ui.renameButton.clicked.connect(self.rename_item)

        self.ui.othersProjectsTreeWidget.itemChanged.connect(self.on_item_changed)
        self.ui.ownProjectsTreeWidget.itemChanged.connect(self.on_item_changed)

    def create_sort_button(self):
        self.sort_button = QToolButton(self)
        self.sort_button.setText("Сортировать")
        self.sort_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.sort_menu = QMenu(self.sort_button)

        self.sort_name_az_action = QAction("По имени А-Я", self)
        self.sort_name_za_action = QAction("По имени Я-А", self)
        self.sort_date_asc_action = QAction("По дате (старые сверху)", self)
        self.sort_date_desc_action = QAction("По дате (новые сверху)", self)

        self.sort_name_az_action.triggered.connect(lambda: self.sort_projects('name_az'))
        self.sort_name_za_action.triggered.connect(lambda: self.sort_projects('name_za'))
        self.sort_date_asc_action.triggered.connect(lambda: self.sort_projects('date_asc'))
        self.sort_date_desc_action.triggered.connect(lambda: self.sort_projects('date_desc'))

        self.sort_menu.addAction(self.sort_name_az_action)
        self.sort_menu.addAction(self.sort_name_za_action)
        self.sort_menu.addAction(self.sort_date_asc_action)
        self.sort_menu.addAction(self.sort_date_desc_action)

        self.sort_button.setMenu(self.sort_menu)
        self.ui.horizontalLayout_3.addWidget(self.sort_button)  # Добавляем кнопку на форму

    def sort_projects(self, mode):
        def sort_tree(tree, sort_key, reverse=False):
            root = tree.invisibleRootItem()
            items = [root.child(i) for i in range(root.childCount())]

            items.sort(key=sort_key, reverse=reverse)
            for i in range(root.childCount()):
                root.removeChild(root.child(0))

            for item in items:
                root.addChild(item)

        def get_name_key(item):
            return item.text(0).lower()

        def get_date_key(item):
            return item.text(1)

        if mode == 'name_az':
            sort_tree(self.personal_tree, get_name_key)
            sort_tree(self.shared_tree, get_name_key)
        elif mode == 'name_za':
            sort_tree(self.personal_tree, get_name_key, reverse=True)
            sort_tree(self.shared_tree, get_name_key, reverse=True)
        elif mode == 'date_asc':
            sort_tree(self.personal_tree, get_date_key)
            sort_tree(self.shared_tree, get_date_key)
        elif mode == 'date_desc':
            sort_tree(self.personal_tree, get_date_key, reverse=True)
            sort_tree(self.shared_tree, get_date_key, reverse=True)

    def on_item_changed(self, item, column):
        if column != 0:
            return
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_data.project_prop = 'name'
        item_data.project_prop_value = item.text(column)
        result = sp.new_update_project_from_record(item_data.table_fit(PROJECT_TABLE))
        self.force_rename(item, result)

    def force_rename(self, item, value):
        self.ui.othersProjectsTreeWidget.itemChanged.disconnect(self.on_item_changed)
        self.ui.ownProjectsTreeWidget.itemChanged.disconnect(self.on_item_changed)
        item.setData(0, Qt.ItemDataRole.UserRole, value)
        self.ui.othersProjectsTreeWidget.itemChanged.connect(self.on_item_changed)
        self.ui.ownProjectsTreeWidget.itemChanged.connect(self.on_item_changed)

    def rename_item(self):
        selected_items = self.ui.ownProjectsTreeWidget.selectedItems()
        tree = self.ui.ownProjectsTreeWidget
        if not selected_items:
            selected_items = self.ui.othersProjectsTreeWidget.selectedItems()
            tree = self.ui.othersProjectsTreeWidget
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Пожалуйста, выберите элемент для переименования.")
            return

        item = selected_items[0]
        tree.editItem(item, 0)

    @property
    def personal_tree(self):
        return self.ui.ownProjectsTreeWidget

    @property
    def shared_tree(self):
        return self.ui.othersProjectsTreeWidget

    @property
    def search_box(self):
        return self.ui.lineEdit

    @property
    def sort_by_date_button(self):
        return self.ui.settingsButton

    def prepare_id_mapping_dict(self, id_mapping):
        return {o.old_id: o.new_id for o in id_mapping}

    def update_ids(self, projects, id_mapping):
        _projects_data = [deepcopy(p.data(0, Qt.ItemDataRole.UserRole)) for p in projects]
        for p in _projects_data:
            p.project_id = id_mapping.get(p.project_id, p.project_id)
            p.project_id_up = id_mapping.get(p.project_id_up, p.project_id_up)
        return _projects_data

    def update_tree(self, projects, root_item=None):
        projects = projects
        # Создаем словарь проектов по их project_id
        projects_by_id = {p.project_id: p for p in projects if p.prop_name == 'name' and not p.deleted}
        children = {}
        # Создаем словарь дочерних элементов для каждого родительского project_id
        for p in projects:
            if p.prop_name == 'name' and not p.deleted:
                children[p.project_id_up] = []
            if p.project_id not in self.project_props:
                self.project_props[p.project_id] = [p]
            else:
                self.project_props[p.project_id].append(p)

        for p in projects:
            if p.prop_name != 'name' or p.deleted:
                continue
            if p.project_id_up:
                children[p.project_id_up].append(p)

        # Добавить элементы с данными в таблицу
        def add_item(project, parent=None):
            item = QTreeWidgetItem([project.prop_value, project.creation_date.strftime('%Y-%m-%d')])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            item.setData(0, Qt.ItemDataRole.UserRole, project)
            item.setData(0, Qt.ItemDataRole.DecorationRole, QIcon(self.icons[project.project_type]))
            if parent:
                parent.addChild(item)
            else:
                if project.project_owner == project.project_author:
                    self.personal_tree.addTopLevelItem(item)
                else:
                    creator_folder = self.find_or_create_folder(self.shared_tree, project.project_author)
                    creator_folder.addChild(item)
            for child in children.get(project.project_id, []):
                add_item(child, item)

        # Добавить корневые элементы в таблицу
        for project in projects_by_id.values():
            if project.project_id_up == (root_item.data(0, Qt.ItemDataRole.UserRole).project_id if root_item else 1):
                add_item(project, root_item)

    def build_tree(self):
        self.personal_tree.clear()
        self.shared_tree.clear()
        self.update_tree(self.projects)

    def find_or_create_folder(self, tree, creator):
        folder_items = tree.findItems(self.users[creator], Qt.MatchFlag.MatchExactly)
        if folder_items:
            return folder_items[0]
        folder_item = QTreeWidgetItem([self.users[creator], ''])
        tree.addTopLevelItem(folder_item)
        return folder_item

    def search_projects(self):
        self.ui.othersProjectsTreeWidget.itemChanged.disconnect(self.on_item_changed)
        self.ui.ownProjectsTreeWidget.itemChanged.disconnect(self.on_item_changed)
        search_term = self.search_box.text().lower()
        is_search_empty = not search_term.strip()

        def match_item(item):
            project = item.data(0, Qt.ItemDataRole.UserRole)
            if project:
                if self.search_mode == 'name':
                    return search_term in project.prop_value.lower()
            return False

        def search_tree(tree):
            def search_children(item, parent_match=False):
                item_match = match_item(item) if not is_search_empty else False
                has_visible_children = False
                for i in range(item.childCount()):
                    child = item.child(i)
                    child_visible = search_children(child, item_match)
                    has_visible_children = has_visible_children or child_visible
                item.setHidden(not (item_match or has_visible_children or is_search_empty or parent_match))
                if item_match and not parent_match:
                    item.setExpanded(True)
                    item.setBackground(0, QBrush(QColor("yellow")))
                else:
                    if item_match:
                        item.setBackground(0, QBrush(QColor("yellow")))
                    else:
                        item.setBackground(0, QBrush(QColor("white")))
                    if is_search_empty:
                        item.setExpanded(False)
                    else:
                        item.setExpanded(True)
                return item_match or has_visible_children

            root = tree.invisibleRootItem()
            for i in range(root.childCount()):
                search_children(root.child(i))

        for tree in [self.personal_tree, self.shared_tree]:
            search_tree(tree)

        self.personal_tree.resizeColumnToContents(0)
        self.shared_tree.resizeColumnToContents(0)

        self.ui.othersProjectsTreeWidget.itemChanged.connect(self.on_item_changed)
        self.ui.ownProjectsTreeWidget.itemChanged.connect(self.on_item_changed)

    def search_item_recursive(self, item, auto_open_id):
        for i in range(item.childCount()):
            child = item.child(i)
            project = child.data(0, Qt.ItemDataRole.UserRole)
            if project and str(project.id) == auto_open_id:
                self.res = project
                return True
            if self.search_item_recursive(child, auto_open_id):
                return True
        return False

    def exec_(self) -> int:
        if self.auto_open():
            return True
        else:
            return super().exec_()

    def auto_open(self):
        def search_tree(tree, auto_open_id):
            root = tree.invisibleRootItem()
            return self.search_item_recursive(root, auto_open_id)

        if search_tree(self.ui.ownProjectsTreeWidget, self.auto_open_id):
            return True

        if search_tree(self.ui.othersProjectsTreeWidget, self.auto_open_id):
            return True

        return False

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.selectButton.clicked.connect(self.select)
        self.ui.createButton.clicked.connect(self.create_project)
        self.ui.removeButton.clicked.connect(self.remove_project)
        self.ui.passProjectButton.clicked.connect(self.pass_project)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.copyButton.clicked.connect(self.copy_project)

        self.ui.othersProjectsTreeWidget.selectionModel().selectionChanged.connect(self.change_selected)
        self.ui.ownProjectsTreeWidget.selectionModel().selectionChanged.connect(self.change_selected)

    def collect_all_children(self, root):
        children = []
        child_count = root.childCount()
        if child_count:
            for i in range(child_count):
                child = root.child(i)
                children.append(child)
                children += self.collect_all_children(child)
        return children

    def copy_project(self):
        root_item = None
        if len(self.ui.ownProjectsTreeWidget.selectedItems()):
            root_item = self.ui.ownProjectsTreeWidget.selectedItems()[0]
        elif len(self.ui.othersProjectsTreeWidget.selectedItems()):
            root_item = self.ui.othersProjectsTreeWidget.selectedItems()[0]
        if not root_item:
            return

        project_items, data_items, graph_id_list = self.collect_selected_project_data()
        id_mapping = sp.pass_project_to_another_user(data_items, graph_id_list,
                                                     root_item.data(0, Qt.ItemDataRole.UserRole).project_id_up,
                                                     self.main_window.user.id)
        if id_mapping:
            print('Передался')
            id_mapping = self.prepare_id_mapping_dict(id_mapping)
            projects = self.update_ids(project_items + [root_item], id_mapping)
            self.update_tree(projects, root_item.parent())
            self.projects += projects

    def collect_selected_project_data(self):
        root_item = None
        if len(self.ui.ownProjectsTreeWidget.selectedItems()):
            root_item = self.ui.ownProjectsTreeWidget.selectedItems()[0]
        elif len(self.ui.othersProjectsTreeWidget.selectedItems()):
            root_item = self.ui.othersProjectsTreeWidget.selectedItems()[0]
        if not root_item:
            return
        project_items = self.collect_all_children(root_item)
        project_items = [item for item in set(project_items) if
                         item.data(0, Qt.ItemDataRole.UserRole).deleted is False or item.data(0, Qt.ItemDataRole.UserRole).deleted == 'False']

        data_items = [obj.table_fit(PROJECT_TABLE) for obj in
                      list(set(self.project_props[root_item.data(0, Qt.ItemDataRole.UserRole).project_id]))]
        graph_id_list = []
        for item in project_items:
            for obj in self.project_props[item.data(0, Qt.ItemDataRole.UserRole).project_id]:
                data_items += [obj.table_fit(PROJECT_TABLE)]
                if obj.project_prop == 'graph_type' and obj.project_prop_value == 'xy':
                    graph_id_list.append(obj.project_id)
        return project_items, data_items, graph_id_list

    def pass_project(self):
        root_item = None
        if len(self.ui.ownProjectsTreeWidget.selectedItems()):
            root_item = self.ui.ownProjectsTreeWidget.selectedItems()[0]
        elif len(self.ui.othersProjectsTreeWidget.selectedItems()):
            root_item = self.ui.othersProjectsTreeWidget.selectedItems()[0]
        if not root_item:
            return
        dialog = UserSelectionDialog()
        if dialog.exec_():
            user = dialog.get_result()
            project_items, data_items, graph_id_list = self.collect_selected_project_data()
            id_mapping = sp.pass_project_to_another_user(data_items, graph_id_list, 1, user._data.id)
            if id_mapping:
                print('Передался')
                if user._data.id == self.main_window.user.id:
                    id_mapping = self.prepare_id_mapping_dict(id_mapping)
                    projects = self.update_ids(project_items + [root_item], id_mapping)
                    self.update_tree(projects)
                    self.projects += projects

    def remove_project(self):
        from app.basic_funcs import get_answer, error
        selected = None
        success = False
        tree = None
        if get_answer('Удаление проекта', 'Вы точно хотите удалить проект полностью?'):
            selected_own = self.ui.ownProjectsTreeWidget.selectedItems()
            selected_other = self.ui.othersProjectsTreeWidget.selectedItems()
            if selected_own:
                tree = self.ui.ownProjectsTreeWidget
                selected = selected_own[0]
                item = selected.data(0, Qt.ItemDataRole.UserRole)
                success = sp.delete_project(item.id, True, True, True)  # TODO проекты удаляются полностью
            elif selected_other:
                tree = self.ui.othersProjectsTreeWidget
                selected = selected_other[0]
                item = selected.data(0, Qt.ItemDataRole.UserRole)
                success = sp.delete_project(item.id, True, True, True)  # TODO проекты удаляются полностью
            if selected is None:
                return
            parent = selected.parent()
            if parent:
                parent.removeChild(selected)
            else:
                tree.takeTopLevelItem(tree.indexOfTopLevelItem(selected))
            if not success:
                error('Ошибка!', 'Не удалось удалить проект.')

    def create_project(self):
        from app.basic_funcs import get_text, error
        project_name = get_text('Создание проекта', 'Напишите название проекта:', 'Новый проект')
        if project_name:
            projects = sp.create_project(project_name)
            for project in projects:
                project.type_ = self.project_types[project.project_type]

            self.update_tree(projects)
            self.projects += projects
        else:
            error('Ошибка при создании проекта!', 'Неверное имя проекта.')

    def select(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""

        selected_own = self.ui.ownProjectsTreeWidget.selectedItems()
        selected_other = self.ui.othersProjectsTreeWidget.selectedItems()

        if selected_own:
            item = selected_own[0].data(0, Qt.ItemDataRole.UserRole)
            self.res = item  # Получаем выбранного пользователя
            self.accept()

        elif selected_other:
            item = selected_other[0].data(0, Qt.ItemDataRole.UserRole)
            self.res = item  # Получаем выбранного пользователя
            self.accept()

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        # search = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        # self.proxy.setFilterRegularExpression(search)  # Применяем регулярное выражение для фильтрации пользователей

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    def change_selected(self, selected: QItemSelection):
        """Обработка изменения выбранного пользователя"""
        if selected.count():
            _selected = selected.indexes()[0]
            item = self.ui.ownProjectsTreeWidget.itemFromIndex(_selected)
            if item.data(0, Qt.ItemDataRole.UserRole).type_ in ['project', 'project_root']:
                self.ui.copyButton.setEnabled(True)
                self.ui.renameButton.setEnabled(True)
                if item.data(0, Qt.ItemDataRole.UserRole).type_ == 'project':
                    self.ui.selectButton.setEnabled(True)
                else:
                    self.ui.selectButton.setEnabled(False)

                self.ui.removeButton.setEnabled(True)
                self.ui.passProjectButton.setEnabled(True)
            else:
                self.ui.copyButton.setEnabled(False)
                self.ui.renameButton.setEnabled(False)
                self.ui.selectButton.setEnabled(False)
                self.ui.removeButton.setEnabled(False)
                self.ui.passProjectButton.setEnabled(False)
        else:
            self.ui.copyButton.setEnabled(False)
            self.ui.renameButton.setEnabled(False)
            self.ui.selectButton.setEnabled(False)
            self.ui.removeButton.setEnabled(False)
            self.ui.passProjectButton.setEnabled(False)

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
