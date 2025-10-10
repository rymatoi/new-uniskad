from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QWidget

from resources.ui.ui_py.ui_settings_appearance import Ui_SettingsAppearance
from resources.ui.ui_py.ui_settings_general import Ui_SettingsGeneral


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


class GeneralTab(QWidget):
    """Вкладка с основными настройками приложения."""

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.mw = main_window
        self.setupUi(Ui_SettingsGeneral())
        self.init_values()
        self.create_connections()

    def setupUi(self, ui):
        widget = QWidget(self)
        widget.ui = ui
        widget.ui.setupUi(widget)
        self.ui = widget.ui

    def create_connections(self):
        self.ui.sessionTimeoutSpinBox.valueChanged.connect(
            lambda: self.prop_changed('application_close_timeout'))
        self.ui.notificationTimeoutSpinBox.valueChanged.connect(
            lambda: self.prop_changed('notifications_timeout'))

    def prop_changed(self, prop_name):
        if self.mw is None:
            return

        if prop_name == 'application_close_timeout':
            timeout = int(self.ui.sessionTimeoutSpinBox.value())
            self.mw.user_settings.set('application_close_timeout', timeout)
        elif prop_name == 'notifications_timeout':
            timeout_seconds = int(self.ui.notificationTimeoutSpinBox.value())
            self.mw.user_settings.set('notifications_timeout', timeout_seconds * 1000)

    def init_values(self):
        timeout = self.mw.user_settings.get('application_close_timeout')
        if timeout is None:
            timeout = 30
        try:
            timeout_value = int(timeout)
        except (TypeError, ValueError):
            timeout_value = 30
        timeout_value = max(timeout_value, self.ui.sessionTimeoutSpinBox.minimum())
        timeout_value = min(timeout_value, self.ui.sessionTimeoutSpinBox.maximum())
        self.ui.sessionTimeoutSpinBox.setValue(timeout_value)

        notifications_timeout = self.mw.user_settings.get('notifications_timeout', getattr(self.mw, 'notifications_timeout', 10000))
        try:
            notifications_seconds = int(notifications_timeout) // 1000
        except (TypeError, ValueError):
            notifications_seconds = getattr(self.mw, 'notifications_timeout', 10000) // 1000
        notifications_seconds = max(notifications_seconds, self.ui.notificationTimeoutSpinBox.minimum())
        notifications_seconds = min(notifications_seconds, self.ui.notificationTimeoutSpinBox.maximum())
        self.ui.notificationTimeoutSpinBox.setValue(notifications_seconds)
