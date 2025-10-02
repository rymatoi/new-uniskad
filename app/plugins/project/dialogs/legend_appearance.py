from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QColorDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from dialogs.base import BaseDialog


class LegendAppearanceDialog(BaseDialog):
    """Диалог настройки внешнего вида легенды."""

    def __init__(self, background: Optional[QColor], border: Optional[QColor], opacity: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки легенды")

        self._background_color = QColor(background) if background is not None else QColor(255, 255, 255)
        self._border_color = QColor(border) if border is not None else QColor(100, 100, 100)
        self._opacity = max(0, min(255, opacity))

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("Цвет фона:"))
        self._background_button = QPushButton()
        self._background_button.setFixedSize(60, 24)
        self._background_button.clicked.connect(self._choose_background_color)
        bg_layout.addWidget(self._background_button)
        layout.addLayout(bg_layout)

        border_layout = QHBoxLayout()
        border_layout.addWidget(QLabel("Цвет контура:"))
        self._border_button = QPushButton()
        self._border_button.setFixedSize(60, 24)
        self._border_button.clicked.connect(self._choose_border_color)
        border_layout.addWidget(self._border_button)
        layout.addLayout(border_layout)

        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Прозрачность:"))
        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(0, 255)
        self._opacity_slider.setValue(self._opacity)
        self._opacity_spin = QSpinBox()
        self._opacity_spin.setRange(0, 255)
        self._opacity_spin.setValue(self._opacity)
        self._opacity_slider.valueChanged.connect(self._opacity_spin.setValue)
        self._opacity_spin.valueChanged.connect(self._opacity_slider.setValue)
        opacity_layout.addWidget(self._opacity_slider)
        opacity_layout.addWidget(self._opacity_spin)
        layout.addLayout(opacity_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self._update_button_styles()

    def _choose_background_color(self):
        color = QColorDialog.getColor(self._background_color, self, "Выберите цвет фона легенды")
        if color.isValid():
            self._background_color = color
            self._update_button_styles()

    def _choose_border_color(self):
        color = QColorDialog.getColor(self._border_color, self, "Выберите цвет контура легенды")
        if color.isValid():
            self._border_color = color
            self._update_button_styles()

    def _update_button_styles(self):
        self._background_button.setStyleSheet(f"background-color: {self._background_color.name()};")
        self._border_button.setStyleSheet(f"background-color: {self._border_color.name()};")

    def accept(self):
        self._opacity = self._opacity_spin.value()
        self.res = {
            'background': QColor(self._background_color),
            'border': QColor(self._border_color),
            'opacity': self._opacity,
        }
        super().accept()
