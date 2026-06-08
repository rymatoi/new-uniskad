from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection
from PySide6.QtWidgets import QDialogButtonBox

from app.plugins.synonym_dictionary.models import SynonymDictionaryTreeModel, StandardNode, SynonymNode
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_parameter_confirmation_dialog import Ui_ParameterConfirmationDialog


class ParameterConfirmDialog(BaseDialog):

    def __init__(self, current, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_ParameterConfirmationDialog()
        self.ui.setupUi(self)
        self.current = current
        self.standards = None  # Выбранный пользователь. Используется для получения информации после выхода из диалога
        standards = [parameter for parameter in sp.get_sprav_names_all() if
                     not parameter.id_permanent_name and parameter.flag_permanent]
        self.model = SynonymDictionaryTreeModel()  # Получение списка пользователей
        self.model.ini_tree(standards)
        self.proxy = QSortFilterProxyModel(self)  # Выставление фильтрации
        self.proxy.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy)  # загрузка полученного списка в виджет
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            False)  # делаем кнопку применения недоступной пока не выбран проект
        # self.ui.treeView.header().setResizeMode(QHeaderView.ResizeToContents)  # Подгоняем колонки под контент

        self.create_connections()  # создаем привязки
        self.decide()

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.select_user)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.ui.lineEdit.textChanged.connect(self.search_line_changed)
        self.ui.treeView.doubleClicked.connect(self.select_user)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.change_selected_user)
        self.ui.standard_radioButton.clicked.connect(self.decide)
        self.ui.synonym_radioButton.clicked.connect(self.decide)

    def decide(self):
        if self.ui.standard_radioButton.isChecked():
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.ui.groupBox.setEnabled(False)
        elif self.ui.synonym_radioButton.isChecked():
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.ui.groupBox.setEnabled(True)

    def source_index(self, index: QModelIndex):
        """Индекс в исходной модели"""
        return self.proxy.mapToSource(index)

    def select_user(self):  # обработка копнки принятия
        """Обработка нажатия кнопки **Выбрать**"""
        if self.ui.standard_radioButton.isChecked():

            sp.set_flag_synonim_sprav_names(self.current.data(), False, None)
            sp.set_flag_permanent_sprav_names(self.current.data())

            self.current = StandardNode(self.current._data.attrs_update({
                'flag_synonim': False,
                'flag_permanent': True,
                'type_': 'standard'
            }))

        elif self.ui.synonym_radioButton.isChecked():
            index = self.ui.treeView.currentIndex()  # Индекс выбранного элемента
            source_index = self.source_index(index)
            self.standard = self.model.nodeFromIndex(source_index)  # Получаем выбранного пользователя

            sp.set_flag_synonim_sprav_names(self.current.data(), True, self.standard.data())
            sp.set_flag_permanent_sprav_names(self.current.data())
            self.current = SynonymNode(self.current._data.attrs_update({
                'flag_synonim': True,
                'flag_permanent': True,
                'id_permanent_name': self.standard._data.id_name,
                'type_': 'synonym'
            }))

        self.accept()

    def search_line_changed(self, text):
        """Изменение содержимого поисковой строки"""
        search = QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.proxy.setFilterRegularExpression(search)  # Применяем регулярное выражение для фильтрации пользователей

    def cancel(self):
        """Обработка кнопки отмены """
        self.standard = None  # Сбросить выбранного пользователя
        self.close()

    def change_selected_user(self, selected: QItemSelection):
        """Обработка изменения выбранного пользователя"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            bool(selected))  # Делаем кнопку Выбрать доступной, если есть выбранный элемент

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
