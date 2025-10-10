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
        self._loading = True
        self.setupUi(Ui_SettingsAppearance())
        self.init_default_values()
        self.init_values()
        self.create_connections()
        self.update_font_controls_enabled()
        self._loading = False

    def setupUi(self, ui):
        widget = QWidget(self)
        widget.ui = ui
        widget.ui.setupUi(widget)
        self.ui = widget.ui

    def create_connections(self):
        self.ui.fontComboBox.currentTextChanged.connect(
            lambda: self.prop_changed('font_name')
        )
        self.ui.fontSizeComboBox.currentTextChanged.connect(
            lambda: self.prop_changed('font_size')
        )
        self.ui.customFontCheckBox.stateChanged.connect(
            lambda _: self.prop_changed('use_custom_font')
        )

    def prop_changed(self, prop_name):
        if self.mw is None or self._loading:
            return

        if prop_name == 'font_name':
            self.mw.user_settings.set('font_name', self.ui.fontComboBox.currentText())
        elif prop_name == 'font_size':
            try:
                font_size = int(self.ui.fontSizeComboBox.currentText())
            except ValueError:
                font_size = self.mw.user_settings.get('font_size')
            self.mw.user_settings.set('font_size', font_size)
        elif prop_name == 'use_custom_font':
            use_custom = self.ui.customFontCheckBox.isChecked()
            self.mw.user_settings.set('use_custom_font', use_custom)
            self.update_font_controls_enabled()

        apply_method = getattr(self.mw, 'apply_user_settings', None)
        if callable(apply_method):
            apply_method()

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.addItems(font_families)

        font_sizes = [str(size) for size in QFontDatabase().pointSizes('Arial')]
        self.ui.fontSizeComboBox.addItems(font_sizes)

    def init_values(self):
        use_custom_font = self.mw.user_settings.get('use_custom_font') if self.mw else False
        if isinstance(use_custom_font, str):
            use_custom_font = use_custom_font.lower() == 'true'
        if use_custom_font is not None:
            self.ui.customFontCheckBox.setChecked(bool(use_custom_font))

        if self.mw is not None:
            font_name = self.mw.user_settings.get('font_name')
        else:
            font_name = None

        if not font_name:
            from PySide2.QtWidgets import QApplication

            font_name = QApplication.instance().font().family()
        if font_name and self.ui.fontComboBox.findText(font_name) == -1:
            self.ui.fontComboBox.insertItem(0, font_name)
        if font_name:
            self.ui.fontComboBox.setCurrentText(font_name)

        if self.mw is not None:
            font_size = self.mw.user_settings.get('font_size')
        else:
            font_size = None
        if not font_size:
            from PySide2.QtWidgets import QApplication

            font_size = QApplication.instance().font().pointSize()
        if font_size and self.ui.fontSizeComboBox.findText(str(font_size)) == -1:
            self.ui.fontSizeComboBox.insertItem(0, str(font_size))
        if font_size:
            self.ui.fontSizeComboBox.setCurrentText(str(font_size))

    def update_font_controls_enabled(self):
        enabled = self.ui.customFontCheckBox.isChecked()
        self.ui.fontComboBox.setEnabled(enabled)
        self.ui.fontSizeComboBox.setEnabled(enabled)
