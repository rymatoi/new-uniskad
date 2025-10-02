from typing import Dict

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QColorDialog,
    QFormLayout,
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

    def __init__(self, legend, parent=None, flags=None):
        super().__init__(parent, flags)
        self.setWindowTitle("Настройки легенды")
        self.legend = legend
        self._appearance = legend.appearance() if legend else {
            'background': QColor(255, 255, 255),
            'border': QColor(100, 100, 100),
            'opacity': 1.0,
        }

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Background color chooser
        self.background_button = QPushButton()
        self.background_button.setFixedSize(60, 24)
        self.background_button.clicked.connect(self._choose_background_color)
        form_layout.addRow(QLabel("Цвет фона"), self.background_button)

        # Border color chooser
        self.border_button = QPushButton()
        self.border_button.setFixedSize(60, 24)
        self.border_button.clicked.connect(self._choose_border_color)
        form_layout.addRow(QLabel("Цвет рамки"), self.border_button)

        # Opacity controls
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.valueChanged.connect(self._sync_opacity_spin)
        opacity_layout.addWidget(self.opacity_slider)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.valueChanged.connect(self._sync_opacity_slider)
        opacity_layout.addWidget(self.opacity_spin)

        form_layout.addRow(QLabel("Непрозрачность, %"), opacity_layout)

        layout.addLayout(form_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._apply_initial_state()

    def _apply_initial_state(self):
        background = self._appearance['background']
        border = self._appearance['border']
        opacity = int(round(self._appearance['opacity'] * 100))

        self._update_button_color(self.background_button, background)
        self._update_button_color(self.border_button, border)
        self.opacity_slider.blockSignals(True)
        self.opacity_spin.blockSignals(True)
        self.opacity_slider.setValue(opacity)
        self.opacity_spin.setValue(opacity)
        self.opacity_slider.blockSignals(False)
        self.opacity_spin.blockSignals(False)

    def _choose_background_color(self):
        color = QColorDialog.getColor(self._appearance['background'], self, "Выберите цвет фона")
        if color.isValid():
            self._appearance['background'] = color
            self._update_button_color(self.background_button, color)

    def _choose_border_color(self):
        color = QColorDialog.getColor(self._appearance['border'], self, "Выберите цвет рамки")
        if color.isValid():
            self._appearance['border'] = color
            self._update_button_color(self.border_button, color)

    def _sync_opacity_spin(self, value: int):
        self.opacity_spin.blockSignals(True)
        self.opacity_spin.setValue(value)
        self.opacity_spin.blockSignals(False)
        self._appearance['opacity'] = value / 100.0

    def _sync_opacity_slider(self, value: int):
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(value)
        self.opacity_slider.blockSignals(False)
        self._appearance['opacity'] = value / 100.0

    @staticmethod
    def _update_button_color(button: QPushButton, color: QColor):
        button.setStyleSheet(f"background-color: {color.name()};")

    def accept(self):
        self.res = self._prepare_result()
        super().accept()

    def _prepare_result(self) -> Dict[str, QColor]:
        return {
            'background': self._appearance['background'],
            'border': self._appearance['border'],
            'opacity': self._appearance['opacity'],
        }

    def get_result(self):
        return self.res
