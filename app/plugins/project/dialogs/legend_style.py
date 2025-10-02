from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QDialog,
    QColorDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class LegendStyleDialog(QDialog):
    """Диалог настройки внешнего вида легенды."""

    def __init__(self, legend, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Настройки легенды")

        self._background_color = QColor(legend.background_color)
        self._border_color = QColor(legend.border_color)
        self._opacity = int(round(legend.opacity * 100))

        self._background_button = QPushButton()
        self._border_button = QPushButton()
        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_label = QLabel()

        self._setup_ui()
        self._update_buttons()
        self._update_opacity_label()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self._background_button.clicked.connect(self._select_background_color)
        form_layout.addRow("Цвет фона", self._background_button)

        self._border_button.clicked.connect(self._select_border_color)
        form_layout.addRow("Цвет контура", self._border_button)

        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(self._opacity)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)

        opacity_widget = QWidget()
        opacity_layout = QVBoxLayout(opacity_widget)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.addWidget(self._opacity_slider)
        opacity_layout.addWidget(self._opacity_label)
        form_layout.addRow("Непрозрачность", opacity_widget)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _select_background_color(self):
        color = QColorDialog.getColor(self._background_color, self, "Выбор цвета фона")
        if color.isValid():
            self._background_color = color
            self._update_buttons()

    def _select_border_color(self):
        color = QColorDialog.getColor(self._border_color, self, "Выбор цвета контура")
        if color.isValid():
            self._border_color = color
            self._update_buttons()

    def _on_opacity_changed(self, value: int):
        self._opacity = value
        self._update_opacity_label()

    def _update_buttons(self):
        self._apply_button_style(self._background_button, self._background_color)
        self._apply_button_style(self._border_button, self._border_color)

    def _update_opacity_label(self):
        self._opacity_label.setText(f"{self._opacity}%")

    @staticmethod
    def _apply_button_style(button: QPushButton, color: QColor):
        text_color = "#000000" if color.lightness() > 128 else "#FFFFFF"
        button.setText(color.name().upper())
        button.setStyleSheet(
            f"QPushButton {{ background-color: {color.name()}; color: {text_color}; }}"
        )

    def get_values(self):
        return (
            QColor(self._background_color),
            QColor(self._border_color),
            max(0.0, min(1.0, self._opacity / 100.0)),
        )
