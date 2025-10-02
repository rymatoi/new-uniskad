from typing import Dict

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QColorDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from dialogs.base import BaseDialog


class LegendStyleDialog(BaseDialog):
    """Диалог настройки внешнего вида легенды."""

    def __init__(self, background: QColor, border: QColor, opacity: float, parent=None, flags=None):
        super().__init__(parent, flags)
        self.setWindowTitle('Настройки легенды')

        self._background = QColor(background)
        self._border = QColor(border)
        self._opacity = int(max(0.0, min(1.0, opacity)) * 100)

        self._create_ui()
        self._update_preview()

    def _create_ui(self):
        layout = QVBoxLayout()

        self.preview = QLabel()
        self.preview.setMinimumHeight(60)
        self.preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview)

        # Background color controls
        bg_layout = QHBoxLayout()
        bg_label = QLabel('Цвет фона:')
        self.bg_button = QPushButton()
        self.bg_button.clicked.connect(self._choose_background)
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_button)
        layout.addLayout(bg_layout)

        # Border color controls
        border_layout = QHBoxLayout()
        border_label = QLabel('Цвет контура:')
        self.border_button = QPushButton()
        self.border_button.clicked.connect(self._choose_border)
        border_layout.addWidget(border_label)
        border_layout.addWidget(self.border_button)
        layout.addLayout(border_layout)

        # Opacity controls
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel('Прозрачность:')
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self._opacity)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.opacity_value_label = QLabel(f'{self._opacity}%')
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value_label)
        layout.addLayout(opacity_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _choose_background(self):
        color = QColorDialog.getColor(self._background, self, 'Выбор цвета фона')
        if color.isValid():
            self._background = color
            self._update_preview()

    def _choose_border(self):
        color = QColorDialog.getColor(self._border, self, 'Выбор цвета контура')
        if color.isValid():
            self._border = color
            self._update_preview()

    def _on_opacity_changed(self, value: int):
        self._opacity = value
        self.opacity_value_label.setText(f'{value}%')
        self._update_preview()

    def _update_preview(self):
        rgba_bg = QColor(self._background)
        rgba_bg.setAlpha(int(self._opacity / 100 * 255))
        rgba_border = QColor(self._border)
        style = (
            f'background-color: rgba({rgba_bg.red()}, {rgba_bg.green()}, {rgba_bg.blue()}, {rgba_bg.alpha()});'
            f' border: 2px solid rgba({rgba_border.red()}, {rgba_border.green()}, {rgba_border.blue()}, 255);'
        )
        self.preview.setStyleSheet(style)
        self.preview.setText('Предпросмотр')

        # Update button styles for clarity
        self.bg_button.setStyleSheet(f'background-color: {self._background.name()};')
        self.bg_button.setText(self._background.name())
        self.border_button.setStyleSheet(
            f'background-color: {self._border.name()}; border: 1px solid black;'
        )
        self.border_button.setText(self._border.name())

    def _on_accept(self):
        self.res = self._build_result()
        self.accept()

    def _build_result(self) -> Dict[str, object]:
        return {
            'background': QColor(self._background),
            'border': QColor(self._border),
            'opacity': self._opacity / 100,
        }
