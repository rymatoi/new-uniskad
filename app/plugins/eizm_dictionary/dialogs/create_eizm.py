from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialogButtonBox

from app.basic_funcs import error
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_create_eizm import Ui_CreateEizmDialog


class CreateEizmDialog(BaseDialog):

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_CreateEizmDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.create_connections()  # Созадем привязки к виджетам
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.create_eizm)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)

    def create_eizm(self):
        name = self.ui.lineEdit.text()
        short_name = self.ui.lineEdit_2.text()
        description = self.ui.plainTextEdit.toPlainText()
        success = sp.new_upd_sprav_eizm_record((None, short_name, name, description))
        if success:
            sprav_eizms = sp.get_sprav_eizm_all()
            self.res = [eizm for eizm in sprav_eizms if eizm.eizm_full == name]
            if not self.res:
                error('Ошибка!', 'Неизвестная ошибка при получении единицы измерения.')
            else:
                self.res = self.res[0]
                self.accept()
        else:
            error('Ошибка!', 'Не удалось создать единицу измерения.')
