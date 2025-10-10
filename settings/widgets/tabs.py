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
        self.ui.fontComboBox.currentTextChanged.connect(self.on_font_name_changed)
        self.ui.fontSizeComboBox.currentTextChanged.connect(self.on_font_size_changed)
        self.ui.customFontCheckBox.toggled.connect(self.on_custom_font_toggled)

    def _set_setting(self, name, value):
        if self.mw is None:
            return
        self.mw.user_settings.set(name, value)

    def on_font_name_changed(self, font_name: str):
        if not font_name:
            return
        self._set_setting('font_name', font_name)

    def on_font_size_changed(self, font_size: str):
        if not font_size:
            return
        try:
            value = int(font_size)
        except (TypeError, ValueError):
            value = font_size
        self._set_setting('font_size', value)

    def on_custom_font_toggled(self, checked: bool):
        self.update_font_controls(checked)
        self._set_setting('use_custom_font', checked)

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.addItems(font_families)

        font_sizes = [str(size) for size in QFontDatabase().pointSizes('Arial')]
        self.ui.fontSizeComboBox.addItems(font_sizes)

    def init_values(self):
        use_custom_font = False
        if self.mw is not None:
            use_custom_font = self.mw.user_settings.get('use_custom_font')
        if isinstance(use_custom_font, str):
            use_custom_font = use_custom_font.lower() == 'true'
        self.ui.customFontCheckBox.setChecked(bool(use_custom_font))
        self.update_font_controls(bool(use_custom_font))

        font_name = self.mw.user_settings.get('font_name') if self.mw else None
        if font_name:
            self.ui.fontComboBox.setCurrentText(font_name)

        font_size = self.mw.user_settings.get('font_size') if self.mw else None
        if font_size:
            self.ui.fontSizeComboBox.setCurrentText(str(font_size))

    def update_font_controls(self, enabled: bool):
        self.ui.fontComboBox.setEnabled(enabled)
        self.ui.fontSizeComboBox.setEnabled(enabled)
