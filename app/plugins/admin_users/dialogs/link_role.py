from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialogButtonBox

from app.plugins.admin_roles.models import AdminRolesTreeModel
from app.plugins.eizm_dictionary.models import EizmDictionaryTreeModel
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_link_eizm_dialog import Ui_LinkEizmDialog
from resources.ui.ui_py.ui_link_role_dialog import Ui_LinkRoleDialog


class LinkRoleDialog(BaseDialog):

    def __init__(self, current, exclude=None, flags=None, *args, **kwargs):
        if exclude is None:
            exclude = []
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_LinkRoleDialog()
        self.ui.setupUi(self)
        self.current = current
        roles = [role for role in sp.get_roles() if
                 role.rolename not in exclude]
        self.model = AdminRolesTreeModel()
        self.model.CHECKABLE = True
        self.model.ini_tree(roles)
        self.model.set_view(self.ui.treeView)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.ui.treeView.setIconSize(QSize(16, 16))
        # self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
        #     False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Подгоняем колонки под контент
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.select_item)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        self.ui.treeView.doubleClicked.connect(self.select_item)
        # self.ui.treeView.selectionModel().selectionChanged.connect(self.change_selected_item)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        return self.proxy.mapToSource(index)

    def select_item(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        selected_roles = [role for role in self.model.checked_list if role._data.id_up == self.model.root_id]
        if not selected_roles:
            self.cancel()

        sp.add_link_user_role_array(self.current._data.id, [role._data.id for role in selected_roles])
        self.res = selected_roles
        self.accept()

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        search = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.proxy.setFilterRegularExpression(search)  # Применяем регулярное выражение для фильтрации пользователей

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
