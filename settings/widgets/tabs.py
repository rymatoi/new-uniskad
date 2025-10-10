from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget
from resources.ui.ui_py.ui_settings_appearance import Ui_SettingsAppearance


class AppearanceTab(QWidget):
    """
    Вкладка для отображения графика.
    """

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.mw = main_window
        self.setupUi(Ui_SettingsAppearance())
        self.init_default_values()
        self.init_values()
        self.create_connections()

    def setupUi(self, ui):
        widget = QWidget(self)
        widget.ui = ui
        widget.ui.setupUi(widget)
        self.ui = widget.ui

    def create_connections(self):
        self.ui.fontComboBox.currentTextChanged.connect(lambda: self.prop_changed('font_name'))
        self.ui.fontSizeComboBox.currentTextChanged.connect(lambda: self.prop_changed('font_size'))
        self.ui.customFontCheckBox.stateChanged.connect(lambda: self.prop_changed('use_custom_font'))
        self.ui.modernUiToggleButton.clicked.connect(self.toggle_modern_ui)

    def prop_changed(self, prop_name):
        if self.mw is None:
            return

        if prop_name == 'font_name':
            self.mw.user_settings.set('font_name', self.ui.fontComboBox.currentText())
        elif prop_name == 'font_size':
            self.mw.user_settings.set('font_size', self.ui.fontSizeComboBox.currentText())
        elif prop_name == 'use_custom_font':
            self.mw.user_settings.set('use_custom_font', self.ui.customFontCheckBox.isChecked())

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.addItems(font_families)

        font_sizes = [str(size) for size in QFontDatabase().pointSizes('Arial')]
        self.ui.fontSizeComboBox.addItems(font_sizes)

    def init_values(self):
        use_custom_font = self.mw.user_settings.get('use_custom_font')
        if isinstance(use_custom_font, str):
            use_custom_font = use_custom_font.lower() == 'true'
        if use_custom_font is not None:
            self.ui.customFontCheckBox.setChecked(bool(use_custom_font))

        font_name = self.mw.user_settings.get('font_name')
        if font_name:
            self.ui.fontComboBox.setCurrentText(font_name)

        font_size = self.mw.user_settings.get('font_size')
        if font_size:
            self.ui.fontSizeComboBox.setCurrentText(str(font_size))

        self.update_modern_ui_button()

    def update_modern_ui_button(self):
        if self.mw is None:
            self.ui.modernUiToggleButton.setEnabled(False)
            return

        is_enabled = self._is_modern_ui_enabled()
        self.ui.modernUiToggleButton.blockSignals(True)
        self.ui.modernUiToggleButton.setChecked(is_enabled)
        self.ui.modernUiToggleButton.setText(
            'Выключить новый интерфейс' if is_enabled else 'Включить новый интерфейс'
        )
        self.ui.modernUiToggleButton.blockSignals(False)

    def toggle_modern_ui(self):
        if self.mw is None:
            return

        new_value = not self._is_modern_ui_enabled()
        self.mw.user_settings.set('enable_modern_ui', new_value)
        if hasattr(self.mw, 'apply_user_interface_theme'):
            self.mw.apply_user_interface_theme()
        self.update_modern_ui_button()

    def _is_modern_ui_enabled(self):
        if self.mw is None:
            return False

        value = self.mw.user_settings.get('enable_modern_ui', False)
        if isinstance(value, str):
            value = value.lower() == 'true'
        return bool(value)
