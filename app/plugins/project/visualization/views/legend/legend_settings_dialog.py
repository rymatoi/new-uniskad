from typing import Dict

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QColorDialog,
)

from dialogs.base import BaseDialog


class LegendSettingsDialog(BaseDialog):
    """Диалог настройки параметров легенды."""

    def __init__(
        self,
        background_color: QColor,
        border_color: QColor,
        background_opacity: float,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки легенды")

        self._background_color = QColor(background_color)
        self._background_color.setAlpha(255)
        self._border_color = QColor(border_color)
        self._border_color.setAlpha(255)
        try:
            opacity = float(background_opacity)
        except (TypeError, ValueError):
            opacity = 1.0
        self._background_opacity = max(0.0, min(1.0, opacity))

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self._background_button = QPushButton()
        self._background_button.clicked.connect(self._choose_background_color)
        self._update_button_color(self._background_button, self._background_color)
        form_layout.addRow(QLabel("Цвет фона"), self._background_button)

        self._border_button = QPushButton()
        self._border_button.clicked.connect(self._choose_border_color)
        self._update_button_color(self._border_button, self._border_color)
        form_layout.addRow(QLabel("Цвет контура"), self._border_button)

        opacity_container = QHBoxLayout()
        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(int(round(self._background_opacity * 100)))
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)

        self._opacity_spinbox = QSpinBox()
        self._opacity_spinbox.setRange(0, 100)
        self._opacity_spinbox.setValue(int(round(self._background_opacity * 100)))
        self._opacity_spinbox.valueChanged.connect(self._opacity_slider.setValue)

        self._opacity_slider.valueChanged.connect(self._opacity_spinbox.setValue)

        self._on_opacity_changed(self._opacity_slider.value())

        opacity_container.addWidget(self._opacity_slider)
        opacity_container.addWidget(self._opacity_spinbox)
        form_layout.addRow(QLabel("Непрозрачность фона"), opacity_container)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _update_button_color(button: QPushButton, color: QColor) -> None:
        button.setStyleSheet(
            "QPushButton {background-color: %s; border: 1px solid #444;}" % color.name()
        )
        button.setText(color.name())

    def _choose_background_color(self) -> None:
        color = QColorDialog.getColor(self._background_color, self, "Выбор цвета фона")
        if color.isValid():
            color.setAlpha(255)
            self._background_color = color
            self._update_button_color(self._background_button, color)

    def _choose_border_color(self) -> None:
        color = QColorDialog.getColor(self._border_color, self, "Выбор цвета контура")
        if color.isValid():
            color.setAlpha(255)
            self._border_color = color
            self._update_button_color(self._border_button, color)

    def _on_opacity_changed(self, value: int) -> None:
        clamped = max(0, min(100, int(value)))
        self._background_opacity = clamped / 100.0

    def accept(self) -> None:
        self.res = self._build_result()
        super().accept()

    def _build_result(self) -> Dict[str, object]:
        return {
            "background_color": QColor(self._background_color),
            "border_color": QColor(self._border_color),
            "background_opacity": float(self._background_opacity),
        }
