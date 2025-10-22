from PySide2.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QCheckBox
)
from PySide2.QtGui import QDoubleValidator


class ExtrapolationDialog(QDialog):
    def __init__(self, forward, backward, min_x, max_x, off, parent=None):
        super(ExtrapolationDialog, self).__init__(parent)

        self.setWindowTitle("Экстраполяция")

        self.forward_value = float(forward) if forward is not None else max_x
        self.backward_value = float(backward) if backward is not None else min_x

        self.res = None

        # Основной layout
        main_layout = QVBoxLayout()

        # Форматированный layout
        form_layout = QFormLayout()

        # Поля ввода
        self.forward_input = QLineEdit(self)
        self.backward_input = QLineEdit(self)

        # Добавляем валидаторы
        double_validator = QDoubleValidator(self)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        double_validator.setDecimals(6)
        self.forward_input.setValidator(double_validator)
        self.backward_input.setValidator(double_validator)

        self.forward_input.setText(self._format_value(self.forward_value))
        self.backward_input.setText(self._format_value(self.backward_value))

        self.off = QCheckBox(self)
        self.off.setChecked(off)
        self.off.setText('')

        # Добавляем метки и поля ввода в формированный layout

        form_layout.addRow("Экстраполяция назад:", self.backward_input)
        form_layout.addRow("Экстраполяция вперёд:", self.forward_input)
        form_layout.addRow("Применить экстраполяцию:", self.off)

        # Кнопки
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("ОК", self)
        cancel_button = QPushButton("Отмена", self)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        # Добавляем формированный layout и кнопки в основной layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def accept(self):
        forward_text = self.forward_input.text()
        backward_text = self.backward_input.text()

        try:
            self.forward_value = float(forward_text)
            self.backward_value = float(backward_text)
        except ValueError:
            QMessageBox.critical(self, "Ошибка ввода", "Пожалуйста, введите правильные числовые значения.")
            return

        self.res = self.get_result()

        super(ExtrapolationDialog, self).accept()

    def get_result(self):
        return self.forward_value, self.backward_value, self.off.isChecked()

    @staticmethod
    def _format_value(value: float) -> str:
        formatted = f"{value:.6f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted or "0"
