from PySide2.QtCore import Qt

from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_column_settings import Ui_ColumnSettingsDialog


class ColumnSettingsDialog(BaseDialog):

    def __init__(self, column, item, parent=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_ColumnSettingsDialog()
        self.ui.setupUi(self)

        self.table_page = parent

        self.val_dict = {
            1: 'Слева',
            4: 'По центру',
            2: 'Справа'
        }

        self.val_dict_r = {
            'Слева': '1',
            'По центру': '4',
            'Справа': '2'
        }
        self.column = column
        self.item = item
        self.table = self.item.tableWidget()
        self.create_connections()
        self.init_values()

    def get_alignment_acc(self):
        return self.table.get_column_prop(self.column, 'alignment', int, 1)

    def init_values(self):
        if alignment := self.get_alignment_acc():
            self.ui.alignComboBox.setCurrentText(self.val_dict[alignment])
        else:
            self.ui.alignComboBox.setCurrentText('Слева')

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.savePushButton.clicked.connect(self.accept)

    def accept(self) -> None:
        self.table_page.update_column_prop(self.column, 'alignment',
                                           self.val_dict_r[self.ui.alignComboBox.currentText()])
        super().accept()

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
