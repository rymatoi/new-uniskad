from PySide2 import QtWidgets

from app.basic_funcs import error
from db import sp
from dialogs.base import BaseDialog
from widgets.password import PasswordEdit


class CreateUserDialog(BaseDialog):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        form_layout = QtWidgets.QFormLayout()

        # Create form fields
        self.username_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit = PasswordEdit()
        # self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.firstname_line_edit = QtWidgets.QLineEdit()
        self.secondname_line_edit = QtWidgets.QLineEdit()
        # self.lastname_line_edit = QtWidgets.QLineEdit()

        # self.description_text_edit = QtWidgets.QTextEdit()
        self.options_combo_box = QtWidgets.QComboBox()
        self.roles = {role.rolename: role for role in sp.get_roles() if
                      role.prop_name == 'name' and role.deleted is False}
        self.options_combo_box.addItems([role for role in self.roles])

        # Add form fields to layout
        form_layout.addRow("Имя пользователя:", self.username_line_edit)
        form_layout.addRow("Пароль:", self.password_line_edit)
        form_layout.addRow("Имя:", self.firstname_line_edit)
        form_layout.addRow("Фамилия:", self.secondname_line_edit)
        # form_layout.addRow("Отчество:", self.description_text_edit)

        # form_layout.addRow("Описание:", self.description_text_edit)
        form_layout.addRow("Роль:", self.options_combo_box)

        # Create button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_user)
        button_box.rejected.connect(self.close)

        # Add layout to dialog
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.setWindowTitle('Добавление пользователя')

    def create_user(self) -> None:
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        firstname = self.firstname_line_edit.text()
        secondname = self.secondname_line_edit.text()
        # lastname = self.lastname_line_edit.text()
        # description = self.description_text_edit.toPlainText()
        required_fields = (
            (secondname, 'Заполните фамилию пользователя'),
            (username, 'Заполните логин пользователя'),
            (password, 'Заполните пароль пользователя'),
        )
        for value, message in required_fields:
            if not value.strip():
                error('Ошибка создания пользователя', message)
                return

        chosen_option = self.options_combo_box.currentText()
        self.res = (50, username, password, secondname, firstname, self.roles[chosen_option].id)
        self.accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
