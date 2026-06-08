from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHeaderView

from app.plugins.base_state.models import TreeModel, Node
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_select_test_params_dialog import Ui_SelectTestParamsDialog


class RowParam:
    type_ = 'param'
    id_up = 0
    id: str
    prop_name = 'name'
    prop_value: str
    base_name: str

    def __init__(self, data):
        self.id = data
        self.prop_value = data
        self.base_name = data


class ParamNode(Node):

    @staticmethod
    def internal_type():
        return 'param'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def get_icon(self, column=0):
        return QIcon(":/alpha.png")

    def data(self, column=0):
        return self._data.prop_value


class TestDataTreeModel(TreeModel):

    def __init__(self):
        super().__init__()
        self.CHECKABLE = True
        # self._root = ProjectRoot(None)  # переопределяем корень
        self.root_id = 0
        # связать тип элемента с классом в программе
        self.register_nodes([ParamNode])


class TestDataSelectionDialog(BaseDialog):

    def __init__(self, param_list, main_window=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_SelectTestParamsDialog()
        self.ui.setupUi(self)
        self.mw = main_window
        params = [RowParam(param) for param in param_list]
        self.model = TestDataTreeModel()  # Получение списка пользователей
        self.model.ini_tree(params)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.model.font_name = self.mw.user_settings.get('font_name')
        self.model.font_size = self.mw.user_settings.get('font_size')
        # self.ui.selectButton.setEnabled(
        #    False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Подгоняем колонки под контент
        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.selectButton.clicked.connect(self.select)
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        self.ui.treeView.doubleClicked.connect(self.select)
        self.ui.selectAllButton.clicked.connect(self.select_all)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        if index:
            return self.proxy.mapToSource(index)

    def select(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        if self.model.CHECKABLE:
            self.res = self.model.checked_list
        else:
            index = self.ui.treeView.selectedIndexes()[0]
            self.res = self.source_index(index).internalPointer()

        self.accept()

    def select_all(self):  # TODO проблема
        if not len(self.model.checked_list) == self.model.rowCount():
            self.model.checkMultipleItems(self.model.get_root_elements(), Qt.CheckState.Checked)
        else:
            self.model.checkMultipleItems(self.model.get_root_elements(), Qt.CheckState.Unchecked)

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
