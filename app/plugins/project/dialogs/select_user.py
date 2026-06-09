from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection

from app.plugins.admin_users.models import AdminUsersTreeModel
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_select_user_dialog import Ui_SelectUserDialog


class UserSelectionDialog(BaseDialog):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_SelectUserDialog()
        self.ui.setupUi(self)
        self.users = [user for user in sp.get_full_users_list() if not user.deleted]

        for user in self.users:
            user.type_ = 'user'

        self.model = AdminUsersTreeModel()  # Получение списка пользователей
        self.model.ini_tree(self.users)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.ui.selectButton.setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Подгоняем колонки под контент
        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.selectButton.clicked.connect(self.select)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.change_selected)
        # self.model.itemChecked.connect(self.change_selected)
        self.ui.treeView.doubleClicked.connect(lambda: None)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        return self.proxy.mapToSource(index)

    def select(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        self.res = self.source_index(self.ui.treeView.selectedIndexes()[0]).internalPointer()
        self.accept()

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        search = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.proxy.setFilterRegularExpression(search)  # Применяем регулярное выражение для фильтрации пользователей

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    def change_selected(self, selected: QItemSelection):
        """Обработка изменения выбранного пользователя"""
        if self.ui.treeView.selectedIndexes():
            self.ui.selectButton.setEnabled(True)
        else:
            self.ui.selectButton.setEnabled(False)

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
