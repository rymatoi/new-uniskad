from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

from app import app_logger
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog
from settings.models import SettingsTreeModel
from settings.data import get_settings_tree
from settings.widgets.tree import SettingsTreeView
from settings.widgets.tabs import AppearanceTab, GeneralTab

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
        self.treeview.set_tab_factories({
            'appearance': AppearanceTab,
            'general': GeneralTab,
        })

        self.create_connections()  # Созадем привязки к виджетам
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.init_tree()

    def init_tree(self):
        self.ui.splitter.replaceWidget(self.ui.splitter.indexOf(self.ui.treeView), self.treeview)
        self.ui.treeView.deleteLater()
        self.treeview.show()
        model = SettingsTreeModel()

        tree_items = get_settings_tree()
        model.ini_tree(tree_items)

        self.treeview.setModel(model)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.cancelPushButton.clicked.connect(self.close)
        self.ui.applyPushButton.clicked.connect(self.apply_changes)

    def accept(self) -> None:
        self.apply_changes()
        super().accept()

    def apply_changes(self) -> None:
        parent = self.parent()
        if parent and hasattr(parent, 'apply_user_settings'):
            parent.apply_user_settings()
