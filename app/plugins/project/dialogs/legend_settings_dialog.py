from __future__ import annotations

from typing import Dict, Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)
from pyqtgraph import ColorButton

from dialogs.base import BaseDialog


class LegendSettingsDialog(BaseDialog):
    """Диалог настройки параметров легенды."""

    def __init__(self, settings: Optional[Dict[str, object]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки легенды")
        self._initial_settings = settings.copy() if settings else {}

        self._create_ui()
        self._load_initial_values()

    def _create_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Цвет фона легенды
        background_layout = QHBoxLayout()
        background_layout.addWidget(QLabel("Цвет фона:"))
        self.background_color_button = ColorButton()
        self.background_color_button.setObjectName("legendBackgroundColorButton")
        background_layout.addWidget(self.background_color_button)
        background_layout.addStretch()
        layout.addLayout(background_layout)

        # Непрозрачность фона
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Непрозрачность:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setSingleStep(5)
        self.opacity_slider.setObjectName("legendOpacitySlider")
        opacity_layout.addWidget(self.opacity_slider, 1)
        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setSuffix(" %")
        self.opacity_spinbox.setObjectName("legendOpacitySpinBox")
        opacity_layout.addWidget(self.opacity_spinbox)
        layout.addLayout(opacity_layout)

        # Параметры рамки
        border_group = QGroupBox("Рамка")
        border_layout = QHBoxLayout(border_group)
        border_layout.addWidget(QLabel("Цвет:"))
        self.border_color_button = ColorButton()
        self.border_color_button.setObjectName("legendBorderColorButton")
        border_layout.addWidget(self.border_color_button)
        border_layout.addSpacing(12)
        border_layout.addWidget(QLabel("Толщина:"))
        self.border_width_spinbox = QSpinBox()
        self.border_width_spinbox.setRange(0, 10)
        self.border_width_spinbox.setObjectName("legendBorderWidthSpinBox")
        border_layout.addWidget(self.border_width_spinbox)
        border_layout.addStretch()
        layout.addWidget(border_group)

        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Синхронизируем слайдер и спинбокс прозрачности
        self.opacity_slider.valueChanged.connect(self.opacity_spinbox.setValue)
        self.opacity_spinbox.valueChanged.connect(self.opacity_slider.setValue)

    def _load_initial_values(self) -> None:
        default_background = QColor(255, 255, 255)
        default_opacity = 100
        default_border_color = QColor(100, 100, 100)
        default_border_width = 1

        background_color = QColor(
            self._initial_settings.get("background_color", default_background)
        )
        opacity = int(
            self._initial_settings.get("background_opacity", default_opacity)
        )
        border_color = QColor(
            self._initial_settings.get("border_color", default_border_color)
        )
        border_width = int(
            self._initial_settings.get("border_width", default_border_width)
        )

        # Цветовая кнопка не поддерживает прозрачность, поэтому используем отдельный контрол
        background_color.setAlpha(255)
        self.background_color_button.setColor(background_color)

        self.opacity_slider.setValue(max(0, min(100, opacity)))
        self.border_color_button.setColor(border_color)
        self.border_width_spinbox.setValue(max(0, min(10, border_width)))

    def accept(self) -> None:  # type: ignore[override]
        background_color = QColor(self.background_color_button.color())
        background_color.setAlpha(255)
        opacity_percent = self.opacity_spinbox.value()
        border_color = QColor(self.border_color_button.color())
        border_width = self.border_width_spinbox.value()

        self.res = {
            "background_color": background_color,
            "background_opacity": opacity_percent,
            "border_color": border_color,
            "border_width": border_width,
        }

        super().accept()

    def get_result(self) -> Dict[str, object]:
        return self.res if self.res is not None else {}
