import typing

from PySide6 import QtWidgets
from PySide6.QtGui import QIcon


class PasswordEdit(QtWidgets.QLineEdit):
    """Строка для ввода пароля."""

    visible_icon = QIcon(":/eye.png")
    hidden_icon = QIcon(":/hidden_eye.png")

    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self._parent = parent
        self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.toggle_password_action = self.addAction(
            self.visible_icon, QtWidgets.QLineEdit.ActionPosition.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.on_toggle_password_action)
        self.password_shown = False

    def on_toggle_password_action(self):
        if not self.password_shown:
            self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.password_shown = True
            self.toggle_password_action.setIcon(self.hidden_icon)
        else:
            self.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.password_shown = False
            self.toggle_password_action.setIcon(self.visible_icon)
