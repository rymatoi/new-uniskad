from app.basic_funcs import to_float
from app.formula import FormulaLineEdit
from db import sp
from dialogs.base import BaseDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from resources.ui.ui_py.ui_row_settings import Ui_RowSettingsDialog


class RowSettingsDialog(BaseDialog):

    def __init__(self, row, item, parent=None, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.table_page = parent
        self.item = item
        self.table = self.item.tableWidget()
        self.ui = Ui_RowSettingsDialog()
        self.ui.setupUi(self)
        self.row = row
        self.combobox_dict = {}

        self._setup_formula_editor()

        self.init_values()
        self.create_connections()

    def _setup_formula_editor(self):
        self.formula_label = QLabel('Формула строки:', self)
        self.formula_edit = FormulaLineEdit(params=self.table.ord_rows, parent=self)
        self.formula_edit.setPlaceholderText('=Введите формулу для всей строки')
        self.ui.formLayout_2.addRow(self.formula_label, self.formula_edit)

    def get_row_acc(self):
        return self.table.get_row_prop(self.row, 'accuracy', int, 2)

    def init_values(self):
        self.ui.nameLineEdit.setText(self.table.get_row_prop(self.row, 'name', str, self.row))

        self.ui.accuracySpinBox.setValue(self.get_row_acc())

        funcs = []
        if getattr(self.table_page, '_formula_delegate', None) is not None:
            funcs = getattr(self.table_page._formula_delegate, 'funcs', [])
        self.formula_edit.set_context(self.table.ord_rows, funcs)
        self.formula_edit.setText(self.table.get_row_prop(self.row, 'row_formula', str, ''))

        self.combobox_dict = {
            'Пусто': ['Пусто'],
            'Кельвин': ['Цельсий'],
            'Цельсий': ['Кельвин'],
            'Кгс/cм2': ['Па'],
            'Па': ['Кгс/cм2'],
        }
        # self.ui.toComboBox_2.addItems(self.combobox_dict.keys())
        self.ui.fromComboBox_2.addItems(self.combobox_dict.keys())
        self.update_comboboxes()

    def recalculate(self, from_, to_):
        plus_val = 0
        multi_val = 0
        if from_ == 'Пусто':
            self.table_page.update_row_prop(self.row, 'plus_value', 0)
            self.table_page.update_row_prop(self.row, 'mul_value', 1)
            return
        elif from_ == 'Кельвин' and to_ == 'Цельсий':
            plus_val = -273
        elif from_ == 'Цельсий' and to_ == 'Кельвин':
            plus_val = 273
        elif from_ == 'Кгс/cм2' and to_ == 'Па':
            multi_val = 98066.5
        elif from_ == 'Па' and to_ == 'Кгс/cм2':
            multi_val = 1 / 98066.5
        if plus_val:
            self.table_page.update_row_prop(self.row, 'plus_value', plus_val)
        elif multi_val:
            self.table_page.update_row_prop(self.row, 'plus_value', 0)
            self.table_page.update_row_prop(self.row, 'mul_value', multi_val)

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.savePushButton.clicked.connect(self.accept)
        self.ui.fromComboBox_2.currentTextChanged.connect(self.update_comboboxes)

    def update_name(self, new_name):
        if self.table.get_row_prop(new_name, 'name', str, '') != self.ui.nameLineEdit.text():
            self.table_page.update_row_prop(self.row, 'name', self.ui.nameLineEdit.text())
            self.table.update_ord_row(new_name, self.row)

    def update_comboboxes(self):
        self.ui.toComboBox_2.clear()
        self.ui.toComboBox_2.addItems(self.combobox_dict[self.ui.fromComboBox_2.currentText()])

    def accept(self) -> None:
        new_name = self.ui.nameLineEdit.text()
        acc = self.ui.accuracySpinBox.value()
        self.table_page.update_row_prop(self.row, 'accuracy', acc)
        self.recalculate(self.ui.fromComboBox_2.currentText(), self.ui.toComboBox_2.currentText())
        formula_text = self.formula_edit.text()
        if formula_text and not formula_text.startswith('='):
            formula_text = f'={formula_text}'
        self.table_page.update_row_prop(self.row, 'row_formula', formula_text)
        self.update_name(new_name)
        self.row = new_name

        model = self.table.model()
        try:
            row_index = self.table.ord_rows.index(new_name)
        except ValueError:
            row_index = None

        if row_index is not None:
            for column_index, column in enumerate(self.table.ord_columns):
                cell = self.table.item(row_index, column_index)
                if cell is None:
                    continue
                cell.key = (new_name, column)
                cell.calculate_formula()
                if cell.has_dependencies():
                    cell.update_dependencies()
                if model is not None:
                    index = model.index(row_index, column_index)
                    model.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

        if getattr(self.table_page, 'refresh_formula_result', None) is not None:
            self.table_page.refresh_formula_result()

        super().accept()

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
