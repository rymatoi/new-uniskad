from typing import Iterable

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout

from app import app_logger
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog
from settings.models import SettingsTreeModel
from settings.widgets.tree import SettingsTreeView
from db.schemas import SettingsItem

logger = app_logger.get_logger(__name__)


class SettingsDialog(BaseDialog):
    """Окно авторизации пользователя"""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.treeview = SettingsTreeView(self, parent)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса

        self._content_layout = QVBoxLayout(self.ui.widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._current_widget = None

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

        try:
            tree_items = sp.get_settings_tree()
        except Exception:
            logger.exception('Не удалось получить дерево настроек из базы данных. Используется набор по умолчанию.')
            tree_items = []

        if not tree_items:
            tree_items = self._default_tree_items()

        model.ini_tree(tree_items)

        self.treeview.setModel(model)
        self.treeview.setHeaderHidden(True)

        selection_model = self.treeview.selectionModel()
        if selection_model is not None:
            selection_model.currentChanged.connect(lambda current, _: self.treeview.open_item(current))

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
        self.parent().user_settings.update()
        super().accept()

    def apply(self) -> None:
        parent = self.parent()
        if parent is not None and hasattr(parent, 'user_settings'):
            parent.user_settings.update()

    def display_settings_tab(self, widget):
        if widget is None:
            return
        self._clear_content_layout()
        widget.setParent(self.ui.widget)
        self._current_widget = widget
        self._content_layout.addWidget(widget)
        widget.show()

    def _clear_content_layout(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)
        self._current_widget = None

    def _clear_layout(self, layout):
        for index in reversed(range(layout.count())):
            item = layout.takeAt(index)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout(child_layout)

    @staticmethod
    def _default_tree_items() -> Iterable[SettingsItem]:
        """Возвращает набор настроек по умолчанию, если сервер не предоставил данные."""
        return [
            SettingsItem(id=1, id_up=0, prop_name='name', prop_value='Общие'),
            SettingsItem(id=1, id_up=0, prop_name='tab', prop_value='general'),
            SettingsItem(id=2, id_up=0, prop_name='name', prop_value='Внешний вид'),
            SettingsItem(id=2, id_up=0, prop_name='tab', prop_value='appearance'),
        ]
