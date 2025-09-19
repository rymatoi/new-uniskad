import asyncio

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from asyncpg import RaiseError

from app import app_logger
from config.config import app
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_login import Ui_UniLoginDialog
from db import session

logger = app_logger.get_logger(__name__)


class LoginDialog(BaseDialog):
    """Окно авторизации пользователя"""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_UniLoginDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса

        self.setWindowIcon(QIcon(":/uniskad.ico"))

        self.ui.messageBox.hide()  # Скрываем расширенные поля для регистрации пользователя
        self.ui.errorBox.hide()  # Скрываем расширенные поля для регистрации пользователя
        self.create_connections()  # Созадем привязки к виджетам
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.loginButton.clicked.connect(self.login)  # нажатие на кнопку входа/регистрации
        self.ui.username.textChanged.connect(self.update_info)
        self.ui.password.textChanged.connect(self.update_info)

    def update_info(self):
        username = self.ui.username.text()
        password = self.ui.password.text()
        if not (username or password):
            self.show_info_message(False, "Введите логин и пароль")
        else:
            self.show_info_message(False, "")

        self.ui.errorBox.setVisible(False)

    def login(self):
        """Авторизация"""
        username = self.ui.username.text()
        password = self.ui.password.text()
        if not (username or password):
            if not username:
                self.show_info_message(True, "Имя пользователя не может быть пустым")
            self.show_info_message(True, "Введите имя пользователя и пароль")
        else:
            self.show_info_message(False, "")
            success = sp.checkuserpassword(username, password)
            if not isinstance(success, RaiseError) and success:
                logger.info('Авторизация прошла успешно.')
                self.accept()
            else:
                if 'Неверный пароль' in str(success):
                    sp.reduce_user_fail_count(username)
                self.show_error(str(success))

    def show_info_message(self, visible: bool, error):
        self.ui.messageBox.setVisible(visible)
        self.ui.messageBox.setText(error or "")

    def show_error(self, msg: str):
        self.ui.errorBox.setVisible(True)
        self.ui.errorBox.setText(msg)
