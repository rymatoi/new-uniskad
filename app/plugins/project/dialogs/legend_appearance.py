from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)
from pyqtgraph import ColorButton

from app.plugins.project.visualization.views.legend.appearance import LegendAppearance
from dialogs.base import BaseDialog


class LegendAppearanceDialog(BaseDialog):
    """Диалог для настройки внешнего вида легенды."""

    def __init__(self, appearance: Optional[LegendAppearance] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Настройки легенды')

        self._appearance = appearance or LegendAppearance.default()

        self.background_button = ColorButton()
        self.background_button.setColor(self._appearance.background)

        self.border_button = ColorButton()
        self.border_button.setColor(self._appearance.border)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(self._appearance.opacity)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 255)
        self.opacity_spin.setValue(self._appearance.opacity)

        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(1, 10)
        self.border_width_spin.setValue(self._appearance.border_width)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self._setup_layout()
        self._connect_signals()

    def _setup_layout(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.addRow('Фон:', self._wrap_widget(self.background_button))
        form_layout.addRow('Контур:', self._wrap_widget(self.border_button))

        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spin)
        form_layout.addRow('Непрозрачность:', opacity_layout)

        form_layout.addRow('Толщина контура:', self.border_width_spin)

        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

    @staticmethod
    def _wrap_widget(widget):
        from PySide2.QtWidgets import QWidget

        wrapper = QWidget()
        container = QHBoxLayout(wrapper)
        container.setContentsMargins(0, 0, 0, 0)
        container.addWidget(widget)
        container.addStretch(1)
        return wrapper

    def _connect_signals(self):
        self.opacity_slider.valueChanged.connect(self.opacity_spin.setValue)
        self.opacity_spin.valueChanged.connect(self.opacity_slider.setValue)
        self.button_box.accepted.connect(self._accept)
        self.button_box.rejected.connect(self.reject)

    def _accept(self):
        background = self.background_button.color()
        border = self.border_button.color()
        opacity = self.opacity_spin.value()
        border_width = self.border_width_spin.value()

        self.res = LegendAppearance(background, border, opacity, border_width)
        self.accept()
