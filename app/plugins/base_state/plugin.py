from PySide2.QtCore import QObject, Qt
from PySide2.QtWidgets import QMessageBox, QTabWidget, QSplitter

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from db import session

logger = app_logger.get_logger(__name__)


class BasePlugin(QObject):
    def __init__(self, parent: "MainWindow"):
        self._parent = parent
        self.main_window = parent
        self.dock_widget_name = ''
        super().__init__()

    def parent(self):
        return self._parent

    def activate(self):
        """Активация плагина."""
        logger.info("Активирован базовый режим.")
        return True

    def deactivate(self):
        """Выполнить действия при деактивации плагина."""
        if session.has_changes:
            warning = QMessageBox(
                QMessageBox.Warning,
                "Хотите сохранить внесенные изменения?",
                "Хотите сохранить внесенные изменения? Если изменения не сохранить, они будут утрачены",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                self._parent
            )
            warning.setWindowModality(Qt.WindowModal)
            warning.button(QMessageBox.Yes).setText("Сохранить")
            warning.button(QMessageBox.No).setText("Не сохранять")
            warning.button(QMessageBox.Cancel).setText("Отмена")

            result = warning.exec_()
            if result == QMessageBox.Yes:
                pass
                #
            elif result == QMessageBox.No:
                return True
            else:
                return False
        else:
            pass
        return True

    def tree_view(self):
        return TreeView(self._parent)

    def set_tree_model(self, model):
        """Применить модель к основному дереву."""
        self.tree_view().setModel(model)
