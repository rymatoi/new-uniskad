from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget
from db import sp
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

    def prop_changed(self, prop_name):
        if prop_name == 'font_name':
            sp.set_user_default_value(None, None, None, 'font_name', self.ui.fontComboBox.currentText())
        elif prop_name == 'font_size':
            sp.set_user_default_value(None, None, None, 'font_size', self.ui.fontSizeComboBox.currentText())
        elif prop_name == 'use_custom_font':
            sp.set_user_default_value(None, None, None, 'use_custom_font', str(self.ui.customFontCheckBox.isChecked()))

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.addItems(font_families)

        font_sizes = [str(size) for size in QFontDatabase().pointSizes('Arial')]
        self.ui.fontSizeComboBox.addItems(font_sizes)

    def init_values(self):
        bool_values = {
            'true': True,
            'false': False
        }
        if self.mw.user_settings.get('use_custom_font'):
            self.ui.customFontCheckBox.setChecked(bool_values[self.mw.user_settings.use_custom_font.lower()])
        if self.mw.user_settings.get('font_name'):
            self.ui.fontComboBox.setCurrentText(self.mw.user_settings.font_name)
        if self.mw.user_settings.get('font_size'):
            self.ui.fontSizeComboBox.setCurrentText(self.mw.user_settings.font_size)
