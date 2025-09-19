from app.basic_funcs import to_float
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_row_settings import Ui_RowSettingsDialog
from resources.ui.ui_recalculate_eizm import Ui_RecalculateEizmDialog


class RecalculateEizmDialog(BaseDialog):

    def __init__(self, item, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.ui = Ui_RecalculateEizmDialog()
        self.ui.setupUi(self)

        self.item = item
        self.ct = self.item.parent
        self.param = self.ct.get_param(self.item.row)

        self.init_values()
        self.create_connections()

    def init_values(self):
        self.combobox_dict = {
            'Кельвин': ['Цельсий'],
            'Цельсий': ['Кельвин'],
            'Кгс/cм2': ['Па'],
            'Па': ['Кгс/cм2'],
        }
        self.ui.toComboBox.addItems(self.combobox_dict.keys())
        self.ui.fromComboBox.addItems(self.combobox_dict.keys())
        self.update_comboboxes()

    def recalculate(self, from_, to_):
        cells = self.ct.get_row(str(self.param))
        plus_val = 0
        multi_val = 0
        if from_ == 'Кельвин' and to_ == 'Цельсий':
            plus_val = -273
        elif from_ == 'Цельсий' and to_ == 'Кельвин':
            plus_val = 273
        elif from_ == 'Кгс/cм2' and to_ == 'Па':
            multi_val = 98066.5
        elif from_ == 'Па' and to_ == 'Кгс/cм2':
            multi_val = 1 / 98066.5
        for cell in cells:
            if plus_val:
                cell.value.prop_value = to_float(cell.value.prop_value) + plus_val
            elif multi_val:
                cell.value.prop_value = to_float(cell.value.prop_value) * multi_val

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.cancelPushButton.clicked.connect(self.cancel)
        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.fromComboBox.currentTextChanged.connect(self.update_comboboxes)

    def update_comboboxes(self):
        self.ui.toComboBox.clear()
        self.ui.toComboBox.addItems(self.combobox_dict[self.ui.fromComboBox.currentText()])

    def accept(self) -> None:
        self.recalculate(self.ui.fromComboBox.currentText(), self.ui.toComboBox.currentText())
        super().accept()

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
