from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_interpolation import Ui_InterpolationDialog
from PySide2.QtWidgets import QColorDialog, QSpinBox, QLabel, QHBoxLayout, QPushButton
from PySide2.QtGui import QColor
import json


class InterpDialog(BaseDialog):
    """Диалог для интерполяции"""
    POLYNOMIAL_TYPES = ['Кубическая', 'Квадратичная']
    
    names_dict = {
        'Кубическая': 'cubic',
        'Квадратичная': 'quadratic'
    }

    def __init__(self, name, parent=None, flags=None, test_id=None):
        super().__init__(parent, flags)

        self.ui = Ui_InterpolationDialog()
        self.ui.setupUi(self)
        self.ui.polyTypeComboBox.addItems([i for i in self.POLYNOMIAL_TYPES])
        self.ui.nameLineEdit.setText(name)
        self.test_id = test_id  # Запоминаем test_id
        
        # Добавляем элементы для настройки линии
        self._add_style_controls()
        
        # Устанавливаем начальный цвет
        self.line_color = QColor('#1f77b4')  # Синий по умолчанию
        self._update_color_button()
        
    def _add_style_controls(self):
        """Добавляет элементы управления для стиля линии"""
        # Выбор толщины линии
        line_width_layout = QHBoxLayout()
        line_width_layout.addWidget(QLabel("Толщина:"))
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setRange(1, 10)
        self.line_width_spin.setValue(2)
        line_width_layout.addWidget(self.line_width_spin)
        self.ui.formLayout.addRow(line_width_layout)
        
        # Выбор цвета
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет:"))
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 20)
        self.color_button.clicked.connect(self._select_color)
        color_layout.addWidget(self.color_button)
        self.ui.formLayout.addRow(color_layout)
        
    def _select_color(self):
        """Открывает диалог выбора цвета"""
        color = QColorDialog.getColor(self.line_color, self, "Выберите цвет линии")
        if color.isValid():
            self.line_color = color
            self._update_color_button()
            
    def _update_color_button(self):
        """Обновляет цвет кнопки"""
        self.color_button.setStyleSheet(f"background-color: {self.line_color.name()};")

    def get_result(self):
        """
        Возвращает результат диалога для создания интерполяции.
        
        Returns:
            str: JSON строка с данными интерполяции.
        """
        if not self.result():
            return None

        name = self.ui.nameLineEdit.text()
        interp_type = self.selected_polynomial_type
        test_id = self.test_id
        
        # Получаем выбранные стили линии
        color = self.line_color.name()
        line_width = self.line_width_spin.value()
        
        return json.dumps({
            "name": name,
            "type": interp_type,
            "test_id": test_id,
            "color": color,
            "line_width": line_width
        })

    @property
    def selected_polynomial_type(self):
        """Выбранный тип полинома."""
        index = self.ui.polyTypeComboBox.currentIndex()
        poly_type = self.POLYNOMIAL_TYPES[index]
        # Преобразуем русское название в английское для библиотеки
        return self.names_dict[poly_type]
