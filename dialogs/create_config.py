from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_create_config import Ui_CreateConfigDialog


class ConfigData:
    rhost: str
    rport: str
    rusername: str
    rpassword: str
    rdatabase: str

    lhost: str
    lport: str
    lusername: str
    lpassword: str
    ldatabase: str

    level = 'INFO'
    filename = 'uniskad.log'


class CreateConfigDialog(BaseDialog):
    """Окно авторизации пользователя"""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_CreateConfigDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.create_connections()  # Созадем привязки к виджетам
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.createPushButton.clicked.connect(self.create_config)

    def create_config(self):
        config_data = ConfigData()
        config_data.rport = self.ui.portLineEdit.text()
        config_data.rhost = self.ui.hostLineEdit.text()
        config_data.rusername = self.ui.usernameLineEdit.text()
        config_data.rdatabase = self.ui.databaseLineEdit.text()
        config_data.rpassword = self.ui.passwordLineEdit.text()

        config_data.lport = self.ui.portLineEdit_2.text()
        config_data.lhost = self.ui.hostLineEdit_2.text()
        config_data.lusername = self.ui.usernameLineEdit_2.text()
        config_data.ldatabase = self.ui.databaseLineEdit_2.text()
        config_data.lpassword = self.ui.passwordLineEdit_2.text()

        self.res = config_data
        self.accept()
