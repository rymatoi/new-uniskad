from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget, QPushButton
from resources.ui.ui_py.ui_settings_appearance import Ui_SettingsAppearance


class AppearanceTab(QWidget):
    """
    Вкладка для отображения графика.
    """

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.mw = main_window
        self.setupUi(Ui_SettingsAppearance())
        self.themeToggleButton = QPushButton(self.tr('Включить интерфейс 2025'))
        self.themeToggleButton.setCheckable(True)
        self.themeToggleButton.setMinimumHeight(36)
        self.ui.gridLayout.removeItem(self.ui.verticalSpacer)
        self.ui.gridLayout.addWidget(self.themeToggleButton, 1, 0, 1, 1)
        self.ui.gridLayout.addItem(self.ui.verticalSpacer, 2, 0, 1, 1)
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
        self.themeToggleButton.clicked.connect(self.toggle_modern_ui)

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

        modern_enabled = self.mw.modern_theme_enabled() if self.mw else False
        self.themeToggleButton.setChecked(modern_enabled)
        self.update_toggle_text(modern_enabled)

    def update_toggle_text(self, enabled: bool) -> None:
        if enabled:
            self.themeToggleButton.setText(self.tr('Вернуться к классическому интерфейсу'))
        else:
            self.themeToggleButton.setText(self.tr('Включить интерфейс 2025'))

    def toggle_modern_ui(self):
        enabled = self.themeToggleButton.isChecked()
        if self.mw:
            self.mw.set_modern_theme_enabled(enabled)
        self.update_toggle_text(enabled)
