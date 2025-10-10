from dataclasses import dataclass
from typing import List

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

from app import app_logger
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog
from settings.models import SettingsTreeModel
from settings.widgets.tree import SettingsTreeView

logger = app_logger.get_logger(__name__)


class SettingsDialog(BaseDialog):
    """Окно авторизации пользователя"""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.treeview = SettingsTreeView(self, parent)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса

        self.ui.horizontalGroupBox.setMaximumHeight(50)
        self.ui.splitter.setSizes([self.width() / 5, self.width() / 2])
        self.setWindowTitle('Настройки')

        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.create_connections()  # Созадем привязки к виджетам
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.init_tree()

    def init_tree(self):
        self.ui.splitter.replaceWidget(self.ui.splitter.indexOf(self.ui.treeView), self.treeview)
        self.ui.treeView.deleteLater()
        self.treeview.show()
        model = SettingsTreeModel()

        tree_items = self._load_tree_items()
        model.ini_tree(tree_items)

        self.treeview.setModel(model)
        if model.rowCount():
            first_index = model.index(0, 0)
            if first_index.isValid():
                self.treeview.setCurrentIndex(first_index)
                self.treeview.open_item(first_index)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.cancelPushButton.clicked.connect(self.close)
        self.ui.applyPushButton.clicked.connect(self.apply)

    def accept(self) -> None:
        self.apply()
        super().accept()

    def apply(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, 'apply_user_settings'):
            parent.apply_user_settings()

    @staticmethod
    def _default_tree_items() -> List['StaticSettingsItem']:
        return [
            StaticSettingsItem(id=1, id_up=0, prop_name='name', prop_value='Общие'),
            StaticSettingsItem(id=1, id_up=0, prop_name='tab_id', prop_value='general'),
            StaticSettingsItem(id=2, id_up=0, prop_name='name', prop_value='Оформление'),
            StaticSettingsItem(id=2, id_up=0, prop_name='tab_id', prop_value='appearance'),
        ]

    def _load_tree_items(self) -> List['StaticSettingsItem']:
        try:
            tree_items = sp.get_settings_tree()
            if tree_items:
                return tree_items
        except Exception:
            logger.exception('Не удалось получить дерево настроек из БД. Используем локальные настройки.')
        return self._default_tree_items()


@dataclass
class StaticSettingsItem:
    id: int
    id_up: int
    prop_name: str
    prop_value: str
    type_: str = 'settings_item'
