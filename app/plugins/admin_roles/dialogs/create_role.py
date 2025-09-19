from PySide2 import QtWidgets

from app.basic_funcs import info, error
from db import sp
from dialogs.base import BaseDialog


class CreateRoleDialog(BaseDialog):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        form_layout = QtWidgets.QFormLayout()

        # Create form fields
        self.rolename_line_edit = QtWidgets.QLineEdit()
        self.description_line_edit = QtWidgets.QTextEdit()

        # Add form fields to layout
        form_layout.addRow("Название роли:", self.rolename_line_edit)
        form_layout.addRow("Описание:", self.description_line_edit)
        # Create button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_role)
        button_box.rejected.connect(self.close)

        # Add layout to dialog
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def create_role(self):
        rolename = self.rolename_line_edit.text()
        description = self.description_line_edit.toPlainText()
        self.res = rolename, description
        self.accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
