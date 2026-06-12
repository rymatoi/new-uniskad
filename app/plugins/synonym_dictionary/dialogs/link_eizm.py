from time import perf_counter

from PySide2.QtCore import QSortFilterProxyModel, QModelIndex, QRegExp, Qt, QItemSelection
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialogButtonBox, QPushButton

from app.plugins.eizm_dictionary.models import EizmDictionaryTreeModel
from app.plugins.base_state.selection_helpers import apply_filter, log_initialized, set_visible_checked
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_link_eizm_dialog import Ui_LinkEizmDialog


class LinkEizmDialog(BaseDialog):

    def __init__(self, current, exclude=None, flags=None, *args, **kwargs):
        if exclude is None:
            exclude = []
        started = perf_counter()
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_LinkEizmDialog()
        self.ui.setupUi(self)
        self.selectAllButton = QPushButton('Выбрать все', self)
        self.clearAllButton = QPushButton('Снять все', self)
        self.ui.buttonBox.addButton(self.selectAllButton, QDialogButtonBox.ActionRole)
        self.ui.buttonBox.addButton(self.clearAllButton, QDialogButtonBox.ActionRole)
        self.current = current
        self.standards = None  # Выбранный пользователь. Используется для получения информации после выхода из диалога
        eizms = [eizm for eizm in sp.get_sprav_eizm_all() if
                 eizm.id_eizm not in exclude and eizm.eizm_short != 'not_set']
        self.model = EizmDictionaryTreeModel()
        self.model.CHECKABLE = True
        self.model.ini_tree(eizms)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeToContents)  # Подгоняем колонки под контент
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.create_connections()  # создаем привязки
        log_initialized(self, len(eizms), started)

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.select_item)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        self.ui.treeView.doubleClicked.connect(self.select_item)
        self.selectAllButton.clicked.connect(self.select_all)
        self.clearAllButton.clicked.connect(self.clear_all)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.change_selected_item)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        return self.proxy.mapToSource(index)

    def select_item(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        selected_eizms = self.model.checked_list

        # sp.add_link_name_eizm(self.current._data.id_name, selected_eizm._data.id_eizm)

        self.res = selected_eizms
        self.accept()

    def select_all(self):
        set_visible_checked(self, Qt.Checked, 'select_all')

    def clear_all(self):
        set_visible_checked(self, Qt.Unchecked, 'clear_all')

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        apply_filter(self, text)

    @staticmethod
    def _selection_filter(text):
        return QRegExp(text, Qt.CaseInsensitive, QRegExp.RegExp)

    def selection_batch_completed(self):
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(bool(self.model.checked_list))

    def cancel(self):
        """Обработка кнопки отмены """
        self.standard = None  # Сбросить выбранного пользователя
        self.close()

    def change_selected_item(self, selected: QItemSelection):
        """Обработка изменения выбранного пользователя"""
        if bool(selected) or len(self.model.checked_list):
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                bool(selected))  # Делаем кнопку Выбрать доступной, если есть выбранный элемент

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
