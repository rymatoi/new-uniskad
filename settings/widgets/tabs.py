from __future__ import annotations

from typing import Optional

from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget

from app.plugins.base_state.widgets import TreeView
from resources.ui.ui_py.ui_settings_appearance import Ui_SettingsAppearance


class AppearanceTab(QWidget):
    """Вкладка настроек отображения интерфейса."""

    DEFAULT_FONT_NAME = 'Times New Roman'
    DEFAULT_FONT_SIZE = 14

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.index = index
        self.tree_view = parent
        self.mw = main_window
        self.setupUi(Ui_SettingsAppearance())
        self.init_default_values()
        self.init_values()
        self.create_connections()
        self.update_font_controls()

    def setupUi(self, ui):
        widget = QWidget(self)
        widget.ui = ui
        widget.ui.setupUi(widget)
        self.ui = widget.ui

    def create_connections(self):
        self.ui.fontComboBox.currentTextChanged.connect(self._on_font_name_changed)
        self.ui.fontSizeComboBox.currentTextChanged.connect(self._on_font_size_changed)
        self.ui.customFontCheckBox.toggled.connect(self._on_custom_font_toggled)

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.clear()
        self.ui.fontComboBox.addItems(font_families)

        font_sizes = [str(size) for size in QFontDatabase().pointSizes('Arial')]
        self.ui.fontSizeComboBox.clear()
        self.ui.fontSizeComboBox.addItems(font_sizes)

    def init_values(self):
        if self.mw is None:
            return

        use_custom_font = self._to_bool(self.mw.user_settings.get('use_custom_font'))
        self.ui.customFontCheckBox.setChecked(use_custom_font)

        font_name = self.mw.user_settings.get('font_name')
        if font_name:
            self.ui.fontComboBox.setCurrentText(font_name)

        font_size = self.mw.user_settings.get('font_size')
        if font_size:
            self.ui.fontSizeComboBox.setCurrentText(str(font_size))

    def update_font_controls(self, enabled: Optional[bool] = None):
        if enabled is None:
            enabled = self.ui.customFontCheckBox.isChecked()
        self.ui.fontComboBox.setEnabled(enabled)
        self.ui.fontSizeComboBox.setEnabled(enabled)

    def _on_font_name_changed(self, text: str):
        if self.mw is None:
            return
        self.mw.user_settings.set('font_name', text)
        self.apply_font_settings()

    def _on_font_size_changed(self, text: str):
        if self.mw is None:
            return
        self.mw.user_settings.set('font_size', text)
        self.apply_font_settings()

    def _on_custom_font_toggled(self, checked: bool):
        if self.mw is None:
            return
        self.mw.user_settings.set('use_custom_font', checked)
        self.update_font_controls(checked)
        self.apply_font_settings()

    def apply_font_settings(self):
        if self.mw is None:
            return

        use_custom_font = self.ui.customFontCheckBox.isChecked()
        font_name = self.ui.fontComboBox.currentText() or self.DEFAULT_FONT_NAME
        font_size = self._to_int(self.ui.fontSizeComboBox.currentText(), default=self.DEFAULT_FONT_SIZE)

        for tree in self.mw.findChildren(TreeView):
            model = tree.model()
            if model is None:
                continue

            if use_custom_font:
                model.font_name = font_name
                model.font_size = font_size
            else:
                model.font_name = self.DEFAULT_FONT_NAME
                model.font_size = self.DEFAULT_FONT_SIZE

            try:
                model.layoutChanged.emit()
            except Exception:
                pass
            tree.viewport().update()

    @staticmethod
    def _to_bool(value: Optional[object]) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {'1', 'true', 't', 'yes', 'y'}
        return bool(value)

    @staticmethod
    def _to_int(value: Optional[object], default: int = 0) -> int:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default
