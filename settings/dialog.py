from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import QApplication

from app import app_logger
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog
from db.user_settings import UserSettings

logger = app_logger.get_logger(__name__)


class SettingsDialog(BaseDialog):
    """Окно локальных настроек приложения."""

    GENERAL_START_MAXIMIZED = 'general/start_maximized'
    GENERAL_REMEMBER_GEOMETRY = 'general/remember_geometry'
    GENERAL_SHOW_STATUS_BAR = 'general/show_status_bar'
    GENERAL_CONFIRM_ON_EXIT = 'general/confirm_on_exit'

    APPEARANCE_CUSTOM_FONT = 'appearance/use_custom_font'
    APPEARANCE_FONT_FAMILY = 'appearance/font_family'
    APPEARANCE_FONT_SIZE = 'appearance/font_size'
    APPEARANCE_THEME = 'appearance/theme'

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Настройки')
        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self._settings = UserSettings()
        self._dirty = False

        self._init_theme_combobox()
        self._defaults = self._build_default_preferences()
        self._load_preferences()

        self.create_connections()

    @staticmethod
    def _coerce_bool(value) -> bool:
        if isinstance(value, str):
            return value.lower() in ('1', 'true', 'yes', 'on')
        return bool(value)

    def _build_default_preferences(self) -> dict:
        app = QApplication.instance()
        default_font = app.font() if app else QFont()
        font_size = default_font.pointSize()
        if font_size <= 0:
            font_size = int(default_font.pointSizeF() or 12)

        return {
            self.GENERAL_START_MAXIMIZED: False,
            self.GENERAL_REMEMBER_GEOMETRY: True,
            self.GENERAL_SHOW_STATUS_BAR: True,
            self.GENERAL_CONFIRM_ON_EXIT: False,
            self.APPEARANCE_CUSTOM_FONT: False,
            self.APPEARANCE_FONT_FAMILY: default_font.family() or '',
            self.APPEARANCE_FONT_SIZE: font_size,
            self.APPEARANCE_THEME: 'system'
        }

    def _init_theme_combobox(self) -> None:
        self.ui.themeComboBox.clear()
        self.ui.themeComboBox.addItem('Системная', 'system')
        self.ui.themeComboBox.addItem('Светлая', 'light')
        self.ui.themeComboBox.addItem('Тёмная', 'dark')

    def _load_preferences(self) -> None:
        preferences = dict(self._defaults)
        bool_keys = {
            self.GENERAL_START_MAXIMIZED,
            self.GENERAL_REMEMBER_GEOMETRY,
            self.GENERAL_SHOW_STATUS_BAR,
            self.GENERAL_CONFIRM_ON_EXIT,
            self.APPEARANCE_CUSTOM_FONT
        }
        for key in list(preferences.keys()):
            stored_value = self._settings.get(key, preferences[key])
            if key in bool_keys:
                stored_value = self._coerce_bool(stored_value)
            elif key == self.APPEARANCE_FONT_SIZE:
                try:
                    stored_value = int(stored_value)
                except (TypeError, ValueError):
                    stored_value = self._defaults[self.APPEARANCE_FONT_SIZE]
            elif stored_value is None:
                stored_value = preferences[key]
            preferences[key] = stored_value

        self._apply_preferences_to_ui(preferences)

    def _apply_preferences_to_ui(self, preferences: dict) -> None:
        self.ui.startMaximizedCheckBox.setChecked(bool(preferences[self.GENERAL_START_MAXIMIZED]))
        self.ui.rememberGeometryCheckBox.setChecked(bool(preferences[self.GENERAL_REMEMBER_GEOMETRY]))
        self.ui.showStatusBarCheckBox.setChecked(bool(preferences[self.GENERAL_SHOW_STATUS_BAR]))
        self.ui.confirmOnExitCheckBox.setChecked(bool(preferences[self.GENERAL_CONFIRM_ON_EXIT]))
        self.ui.customFontCheckBox.setChecked(bool(preferences[self.APPEARANCE_CUSTOM_FONT]))

        font_family = preferences[self.APPEARANCE_FONT_FAMILY]
        if font_family:
            index = self.ui.fontComboBox.findText(font_family, Qt.MatchFixedString)
            if index >= 0:
                self.ui.fontComboBox.setCurrentIndex(index)
        font_size = int(preferences[self.APPEARANCE_FONT_SIZE])
        self.ui.fontSizeSpinBox.setValue(font_size)

        theme_value = preferences[self.APPEARANCE_THEME]
        theme_index = self.ui.themeComboBox.findData(theme_value)
        if theme_index < 0:
            theme_index = 0
        self.ui.themeComboBox.setCurrentIndex(theme_index)

        self._update_font_controls_state(self.ui.customFontCheckBox.isChecked())
        self._dirty = False
        self.ui.applyPushButton.setEnabled(False)

    def _collect_preferences_from_ui(self) -> dict:
        return {
            self.GENERAL_START_MAXIMIZED: self.ui.startMaximizedCheckBox.isChecked(),
            self.GENERAL_REMEMBER_GEOMETRY: self.ui.rememberGeometryCheckBox.isChecked(),
            self.GENERAL_SHOW_STATUS_BAR: self.ui.showStatusBarCheckBox.isChecked(),
            self.GENERAL_CONFIRM_ON_EXIT: self.ui.confirmOnExitCheckBox.isChecked(),
            self.APPEARANCE_CUSTOM_FONT: self.ui.customFontCheckBox.isChecked(),
            self.APPEARANCE_FONT_FAMILY: self.ui.fontComboBox.currentFont().family(),
            self.APPEARANCE_FONT_SIZE: int(self.ui.fontSizeSpinBox.value()),
            self.APPEARANCE_THEME: self.ui.themeComboBox.currentData() or 'system'
        }

    def _update_font_controls_state(self, enabled: bool) -> None:
        self.ui.fontComboBox.setEnabled(enabled)
        self.ui.fontSizeSpinBox.setEnabled(enabled)

    def _mark_dirty(self) -> None:
        if not self._dirty:
            self._dirty = True
            self.ui.applyPushButton.setEnabled(True)

    def create_connections(self):
        """Функция создания привязок"""
        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.cancelPushButton.clicked.connect(self.reject)
        self.ui.applyPushButton.clicked.connect(self.apply)
        self.ui.customFontCheckBox.toggled.connect(self._update_font_controls_state)

        self.ui.startMaximizedCheckBox.toggled.connect(self._mark_dirty)
        self.ui.rememberGeometryCheckBox.toggled.connect(self._mark_dirty)
        self.ui.showStatusBarCheckBox.toggled.connect(self._mark_dirty)
        self.ui.confirmOnExitCheckBox.toggled.connect(self._mark_dirty)
        self.ui.customFontCheckBox.toggled.connect(self._mark_dirty)
        self.ui.fontComboBox.currentFontChanged.connect(lambda *_: self._mark_dirty())
        self.ui.fontSizeSpinBox.valueChanged.connect(lambda *_: self._mark_dirty())
        self.ui.themeComboBox.currentIndexChanged.connect(lambda *_: self._mark_dirty())

    def apply(self) -> None:
        preferences = self._collect_preferences_from_ui()
        for key, value in preferences.items():
            self._settings.set(key, value)

        parent = self.parent()
        if parent is not None and hasattr(parent, 'apply_user_preferences'):
            try:
                parent.apply_user_preferences(preferences)
            except Exception:
                logger.exception('Не удалось применить настройки к интерфейсу.')

        self._dirty = False
        self.ui.applyPushButton.setEnabled(False)

    def accept(self) -> None:
        if self._dirty:
            self.apply()
        super().accept()
