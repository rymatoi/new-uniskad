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
        self.ui.modernUiButton.clicked.connect(self.toggle_modern_ui)

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

        modern_ui = self.mw._get_bool_setting('use_modern_ui', False)
        self.ui.modernUiButton.setChecked(modern_ui)
        self.update_modern_ui_button_text(modern_ui)

    def update_modern_ui_button_text(self, enabled: bool) -> None:
        self.ui.modernUiButton.setText(
            'Интерфейс 2025: включён' if enabled else 'Интерфейс 2025: выключен'
        )

    def toggle_modern_ui(self, checked: bool) -> None:
        if self.mw is None:
            return
        self.mw.apply_modern_ui(checked)
        self.ui.modernUiButton.setChecked(checked)
        self.update_modern_ui_button_text(checked)
