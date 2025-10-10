from PySide2.QtCore import Qt
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QFormLayout, QLabel, QSpinBox, QVBoxLayout, QWidget
from resources.ui.ui_py.ui_settings_appearance import Ui_SettingsAppearance


class AppearanceTab(QWidget):
    """
    Вкладка для отображения графика.
    """

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.mw = main_window
        self._updating_font_controls = False
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
        self.ui.fontComboBox.currentTextChanged.connect(self._on_font_family_changed)
        self.ui.fontSizeComboBox.currentTextChanged.connect(lambda: self.prop_changed('font_size'))
        self.ui.customFontCheckBox.stateChanged.connect(lambda state: self._on_custom_font_changed(state == Qt.Checked))

    def prop_changed(self, prop_name):
        if self.mw is None:
            return

        if prop_name == 'font_name':
            self.mw.user_settings.set('font_name', self.ui.fontComboBox.currentText())
        elif prop_name == 'font_size':
            current_text = self.ui.fontSizeComboBox.currentText()
            if current_text:
                try:
                    self.mw.user_settings.set('font_size', int(current_text))
                except ValueError:
                    self.mw.user_settings.set('font_size', current_text)
        elif prop_name == 'use_custom_font':
            self.mw.user_settings.set('use_custom_font', self.ui.customFontCheckBox.isChecked())

        if hasattr(self.mw, 'apply_user_settings'):
            self.mw.apply_user_settings()

    def init_default_values(self):
        font_families = QFontDatabase().families()
        self.ui.fontComboBox.addItems(font_families)

        self._populate_font_sizes(self.ui.fontComboBox.currentText())

    def init_values(self):
        use_custom_font = self.mw.user_settings.get('use_custom_font')
        if isinstance(use_custom_font, str):
            use_custom_font = use_custom_font.lower() == 'true'
        if use_custom_font is not None:
            self.ui.customFontCheckBox.setChecked(bool(use_custom_font))

        font_name = self.mw.user_settings.get('font_name')
        if font_name:
            index = self.ui.fontComboBox.findText(font_name)
            if index >= 0:
                self.ui.fontComboBox.setCurrentIndex(index)
            else:
                self.ui.fontComboBox.setCurrentText(font_name)

        font_size = self.mw.user_settings.get('font_size')
        if font_size:
            self.ui.fontSizeComboBox.setCurrentText(str(font_size))

        self._update_font_controls_state()

    def _populate_font_sizes(self, family: str):
        if self._updating_font_controls:
            return
        self._updating_font_controls = True
        try:
            self.ui.fontSizeComboBox.blockSignals(True)
            current_size = self.ui.fontSizeComboBox.currentText()
            self.ui.fontSizeComboBox.clear()
            sizes = QFontDatabase().pointSizes(family) or QFontDatabase().standardSizes()
            self.ui.fontSizeComboBox.addItems([str(size) for size in sizes])
            if current_size:
                index = self.ui.fontSizeComboBox.findText(current_size)
                if index >= 0:
                    self.ui.fontSizeComboBox.setCurrentIndex(index)
        finally:
            self.ui.fontSizeComboBox.blockSignals(False)
            self._updating_font_controls = False

    def _update_font_controls_state(self):
        use_custom_font = self.ui.customFontCheckBox.isChecked()
        self.ui.fontComboBox.setEnabled(use_custom_font)
        self.ui.fontSizeComboBox.setEnabled(use_custom_font)

    def _on_font_family_changed(self, family: str):
        if not family:
            return
        self._populate_font_sizes(family)
        self.prop_changed('font_name')

    def _on_custom_font_changed(self, checked: bool):
        if self.mw is None:
            return
        self.ui.customFontCheckBox.blockSignals(True)
        self.ui.customFontCheckBox.setChecked(checked)
        self.ui.customFontCheckBox.blockSignals(False)
        self._update_font_controls_state()
        self.mw.user_settings.set('use_custom_font', checked)
        if hasattr(self.mw, 'apply_user_settings'):
            self.mw.apply_user_settings()


class GeneralTab(QWidget):
    """Вкладка с основными настройками приложения."""

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.mw = main_window
        self.timeoutSpinBox = QSpinBox(self)
        self.timeoutSpinBox.setRange(1, 240)
        self.timeoutSpinBox.setSuffix(' мин')
        self.timeoutSpinBox.setSingleStep(5)

        timeout_label = QLabel('Таймер автоматического выхода:', self)

        form_layout = QFormLayout()
        form_layout.addRow(timeout_label, self.timeoutSpinBox)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addStretch(1)

        self.setLayout(layout)

        self.init_values()
        self.create_connections()

    def init_values(self):
        if self.mw is None:
            return
        timeout = self.mw.user_settings.get('application_close_timeout', 30)
        try:
            timeout = int(timeout)
        except (TypeError, ValueError):
            timeout = 30
        self.timeoutSpinBox.setValue(timeout)

    def create_connections(self):
        self.timeoutSpinBox.valueChanged.connect(self._on_timeout_changed)

    def _on_timeout_changed(self, value: int):
        if self.mw is None:
            return
        self.mw.user_settings.set('application_close_timeout', value)
        if hasattr(self.mw, 'apply_user_settings'):
            self.mw.apply_user_settings()
