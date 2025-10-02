from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QColorDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from dialogs.base import BaseDialog


def _color_to_rgba_string(color: QColor) -> str:
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"


class LegendSettingsDialog(BaseDialog):
    """Диалог настройки внешнего вида легенды."""

    def __init__(
        self,
        background: Optional[QColor] = None,
        border_color: Optional[QColor] = None,
        border_width: float = 1.0,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Настройки легенды")

        self._background = QColor(background or QColor(255, 255, 255, 255))
        if self._background.alpha() == 0:
            self._background.setAlpha(255)

        self._border_color = QColor(border_color or QColor(100, 100, 100))
        if self._border_color.alpha() == 0:
            self._border_color.setAlpha(255)

        self._border_width = float(border_width)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # Background color controls
        bg_layout = QHBoxLayout()
        self.bg_preview = QLabel()
        self.bg_preview.setFixedSize(48, 24)
        self.bg_preview.setStyleSheet(f"background-color: {_color_to_rgba_string(self._background)};")

        self.bg_button = QPushButton("Выбрать цвет")
        self.bg_button.clicked.connect(self._select_background_color)

        bg_layout.addWidget(self.bg_preview)
        bg_layout.addWidget(self.bg_button)
        bg_layout.addStretch()
        form_layout.addRow("Цвет фона:", bg_layout)

        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(self._background.alpha())

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 255)
        self.opacity_spin.setValue(self._background.alpha())

        self.opacity_slider.valueChanged.connect(self.opacity_spin.setValue)
        self.opacity_spin.valueChanged.connect(self.opacity_slider.setValue)
        self.opacity_slider.valueChanged.connect(self._update_background_preview)

        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spin)
        form_layout.addRow("Непрозрачность:", opacity_layout)

        # Border color controls
        border_layout = QHBoxLayout()
        self.border_preview = QLabel()
        self.border_preview.setFixedSize(48, 24)
        self.border_preview.setStyleSheet(
            f"background-color: {_color_to_rgba_string(self._border_color)}; border: 1px solid #000;"
        )

        self.border_button = QPushButton("Цвет контура")
        self.border_button.clicked.connect(self._select_border_color)

        border_layout.addWidget(self.border_preview)
        border_layout.addWidget(self.border_button)
        border_layout.addStretch()
        form_layout.addRow("Контур легенды:", border_layout)

        # Border width
        self.border_width_spin = QDoubleSpinBox()
        self.border_width_spin.setRange(0.0, 10.0)
        self.border_width_spin.setSingleStep(0.5)
        self.border_width_spin.setDecimals(1)
        self.border_width_spin.setValue(max(0.0, self._border_width))
        form_layout.addRow("Толщина контура:", self.border_width_spin)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _select_background_color(self) -> None:
        color = QColorDialog.getColor(self._background, self, "Выбор цвета фона")
        if color.isValid():
            color.setAlpha(self.opacity_spin.value())
            self._background = color
            self._update_background_preview()

    def _select_border_color(self) -> None:
        color = QColorDialog.getColor(self._border_color, self, "Выбор цвета контура")
        if color.isValid():
            if color.alpha() == 0:
                color.setAlpha(255)
            self._border_color = color
            self.border_preview.setStyleSheet(
                f"background-color: {_color_to_rgba_string(self._border_color)}; border: 1px solid #000;"
            )

    def _update_background_preview(self) -> None:
        updated = QColor(self._background)
        updated.setAlpha(self.opacity_spin.value())
        self._background = updated
        self.bg_preview.setStyleSheet(f"background-color: {_color_to_rgba_string(self._background)};")

    def accept(self) -> None:
        self._background.setAlpha(self.opacity_spin.value())
        self.res = {
            'background': QColor(self._background),
            'border_color': QColor(self._border_color),
            'border_width': float(self.border_width_spin.value()),
        }
        super().accept()

    def reject(self) -> None:
        self.res = None
        super().reject()
