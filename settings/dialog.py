from typing import List

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

from app import app_logger
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog
from settings.models import SettingsDefinition, SettingsTreeModel
from settings.widgets.tree import SettingsTreeView
from settings.widgets.tabs import AppearanceTab

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
        model.build_from_definitions(self._create_settings_definitions())

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
        self.ui.applyPushButton.clicked.connect(self.apply_settings)

    def accept(self) -> None:
        self.apply_settings()
        super().accept()

    def apply_settings(self) -> None:
        parent = self.parent()
        if parent is not None and hasattr(parent, 'user_settings'):
            parent.user_settings.update()

    @staticmethod
    def _create_settings_definitions() -> List[SettingsDefinition]:
        return [
            SettingsDefinition(
                identifier=1,
                parent_id=0,
                title='Внешний вид',
                properties={'tab_class': AppearanceTab},
            ),
        ]
