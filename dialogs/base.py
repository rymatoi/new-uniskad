from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class BaseDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags or Qt.WindowFlags())
        self.res = None  # Данные, возвращаемые из диалога
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        if not flags:
            flags = self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
            self.setWindowFlags(flags)

    def get_result(self) -> Any:
        return self.res

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
