from PySide2.QtCore import QSortFilterProxyModel, QModelIndex, QRegExp, Qt, QItemSelection

from app.plugins.work_data.models import WorkDataTreeModel
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_select_test_dialog import Ui_SelectTestDialog


class ProjectTestSelectionDialog(BaseDialog):

    def __init__(self, folder_id, main_window=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        dc = main_window.data_cache
        self.ui = Ui_SelectTestDialog()
        self.ui.setupUi(self)
        self.products = sp.get_all_project_products(folder_id)

        product_types_dict = dc.get_project_types()

        for product in self.products:
            product.type_ = product_types_dict[product.project_type]

        self.model = WorkDataTreeModel()  # Получение списка пользователей
        self.model.CHECKABLE = True
        self.model.root_id = folder_id
        self.model.ini_tree(self.products)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.ui.selectButton.setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeToContents)  # Подгоняем колонки под контент
        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.selectButton.clicked.connect(self.select)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        # self.ui.treeView.selectionModel().selectionChanged.connect(self.change_selected)
        self.model.itemChecked.connect(self.change_selected)
        self.ui.treeView.doubleClicked.connect(lambda: None)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        return self.proxy.mapToSource(index)

    def select(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        self.res = self.model.checked_list  # Получаем выбранного пользователя
        self.accept()

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        search = QRegExp(text, Qt.CaseInsensitive, QRegExp.RegExp)
        self.proxy.setFilterRegExp(search)  # Применяем регулярное выражение для фильтрации пользователей

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    def change_selected(self, selected: QItemSelection):
        """Обработка изменения выбранного пользователя"""
        if len(self.model.checked_list) > 0:
            self.ui.selectButton.setEnabled(True)
        else:
            self.ui.selectButton.setEnabled(False)

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
