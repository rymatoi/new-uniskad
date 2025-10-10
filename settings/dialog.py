from __future__ import annotations
from typing import Any

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QListWidgetItem

from app import app_logger
from db.user_settings import UserSettings
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_settings import Ui_SettingsDialog

logger = app_logger.get_logger(__name__)


class SettingsDialog(BaseDialog):
    """Диалог локальных настроек приложения."""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.setWindowTitle('Настройки')

        self._loading = False
        self._dirty = False

        self.user_settings = getattr(parent, 'user_settings', UserSettings())
        self.parent_window = parent

        self._register_choice_values()
        self._configure_list_widget()
        self._load_values()

        self.create_connections()

    # region helpers
    def _register_choice_values(self) -> None:
        self.ui.fontSizeComboBox.setItemData(0, 'small')
        self.ui.fontSizeComboBox.setItemData(1, 'normal')
        self.ui.fontSizeComboBox.setItemData(2, 'large')

        self.ui.themeComboBox.setItemData(0, 'light')
        self.ui.themeComboBox.setItemData(1, 'dark')

    def _configure_list_widget(self) -> None:
        for row in range(self.ui.categoryListWidget.count()):
            item = self.ui.categoryListWidget.item(row)
            if isinstance(item, QListWidgetItem):
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ui.categoryListWidget.setCurrentRow(0)
        self.ui.stackedWidget.setCurrentIndex(0)

    def _set_apply_enabled(self, enabled: bool) -> None:
        self._dirty = enabled
        self.ui.applyPushButton.setEnabled(enabled)

    @staticmethod
    def _coerce_bool(value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if value in (None, '', Qt.Unchecked):
            return default
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {'1', 'true', 'yes', 'y', 'on'}:
                return True
            if lowered in {'0', 'false', 'no', 'n', 'off'}:
                return False
        return default

    @staticmethod
    def _coerce_int(value: Any, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _set_combobox_by_value(self, combo_box, value: str, default: str) -> None:
        for index in range(combo_box.count()):
            data = combo_box.itemData(index)
            if data == value:
                combo_box.setCurrentIndex(index)
                return
        for index in range(combo_box.count()):
            if combo_box.itemData(index) == default:
                combo_box.setCurrentIndex(index)
                return
        combo_box.setCurrentIndex(0)

    def _current_combobox_value(self, combo_box, fallback: str) -> str:
        data = combo_box.currentData()
        if isinstance(data, str) and data:
            return data
        text = combo_box.currentText()
        return text if text else fallback

    def _load_values(self) -> None:
        self._loading = True

        auto_close = self._coerce_bool(self.user_settings.get('general/auto_close_enabled', True), True)
        timeout_default = self.user_settings.get('application_close_timeout', 30)
        close_timeout = self._coerce_int(
            self.user_settings.get('general/close_timeout_minutes', timeout_default),
            self._coerce_int(timeout_default, 30)
        )
        remember_window = self._coerce_bool(self.user_settings.get('general/save_window_state', True), True)
        restore_session = self._coerce_bool(self.user_settings.get('general/restore_last_session', True), True)
        show_status_bar = self._coerce_bool(self.user_settings.get('interface/show_status_bar', True), True)
        font_size = self.user_settings.get('interface/font_size', 'normal')
        theme = self.user_settings.get('interface/theme', 'light')
        notifications_enabled = self._coerce_bool(
            self.user_settings.get('notifications/enable', True), True)
        timeout_seconds = self._coerce_int(
            self.user_settings.get('notifications/timeout_seconds', 10), 10)

        self.ui.autoCloseCheckBox.setChecked(auto_close)
        self.ui.closeTimeoutSpinBox.setValue(max(1, close_timeout))
        self.ui.saveWindowStateCheckBox.setChecked(remember_window)
        self.ui.restoreSessionCheckBox.setChecked(restore_session)
        self.ui.showStatusBarCheckBox.setChecked(show_status_bar)
        self._set_combobox_by_value(self.ui.fontSizeComboBox, font_size, 'normal')
        self._set_combobox_by_value(self.ui.themeComboBox, theme, 'light')
        self.ui.enableNotificationsCheckBox.setChecked(notifications_enabled)
        self.ui.notificationsTimeoutSpinBox.setValue(max(1, timeout_seconds))

        self._update_auto_close_state(auto_close)
        self._update_restore_state_enabled(remember_window)
        self._update_notifications_state(notifications_enabled)

        self._set_apply_enabled(False)
        self._loading = False

    # endregion

    def create_connections(self):
        self.ui.categoryListWidget.currentRowChanged.connect(self.ui.stackedWidget.setCurrentIndex)

        self.ui.autoCloseCheckBox.toggled.connect(self._update_auto_close_state)
        self.ui.autoCloseCheckBox.toggled.connect(self._mark_dirty)
        self.ui.closeTimeoutSpinBox.valueChanged.connect(self._mark_dirty)

        self.ui.saveWindowStateCheckBox.toggled.connect(self._update_restore_state_enabled)
        self.ui.saveWindowStateCheckBox.toggled.connect(self._mark_dirty)
        self.ui.restoreSessionCheckBox.toggled.connect(self._mark_dirty)

        self.ui.showStatusBarCheckBox.toggled.connect(self._mark_dirty)
        self.ui.fontSizeComboBox.currentIndexChanged.connect(self._mark_dirty)
        self.ui.themeComboBox.currentIndexChanged.connect(self._mark_dirty)

        self.ui.enableNotificationsCheckBox.toggled.connect(self._update_notifications_state)
        self.ui.enableNotificationsCheckBox.toggled.connect(self._mark_dirty)
        self.ui.notificationsTimeoutSpinBox.valueChanged.connect(self._mark_dirty)

        self.ui.acceptPushButton.clicked.connect(self.accept)
        self.ui.cancelPushButton.clicked.connect(self.reject)
        self.ui.applyPushButton.clicked.connect(self.apply_changes)

    # slots / actions
    def _update_auto_close_state(self, checked: bool) -> None:
        self.ui.closeTimeoutLabel.setEnabled(checked)
        self.ui.closeTimeoutSpinBox.setEnabled(checked)

    def _update_restore_state_enabled(self, checked: bool) -> None:
        self.ui.restoreSessionCheckBox.setEnabled(checked)

    def _update_notifications_state(self, checked: bool) -> None:
        self.ui.notificationsTimeoutLabel.setEnabled(checked)
        self.ui.notificationsTimeoutSpinBox.setEnabled(checked)

    def _mark_dirty(self) -> None:
        if self._loading:
            return
        self._set_apply_enabled(True)

    def _save_settings(self) -> None:
        auto_close = self.ui.autoCloseCheckBox.isChecked()
        timeout_minutes = self.ui.closeTimeoutSpinBox.value()
        remember_window = self.ui.saveWindowStateCheckBox.isChecked()
        restore_session = self.ui.restoreSessionCheckBox.isChecked()
        show_status_bar = self.ui.showStatusBarCheckBox.isChecked()
        font_size = self._current_combobox_value(self.ui.fontSizeComboBox, 'normal')
        theme = self._current_combobox_value(self.ui.themeComboBox, 'light')
        notifications_enabled = self.ui.enableNotificationsCheckBox.isChecked()
        notifications_timeout = self.ui.notificationsTimeoutSpinBox.value()

        self.user_settings.set('general/auto_close_enabled', auto_close)
        self.user_settings.set('general/close_timeout_minutes', timeout_minutes)
        self.user_settings.set('application_close_timeout', timeout_minutes)
        self.user_settings.set('general/save_window_state', remember_window)
        self.user_settings.set('general/restore_last_session', restore_session)
        self.user_settings.set('interface/show_status_bar', show_status_bar)
        self.user_settings.set('interface/font_size', font_size)
        self.user_settings.set('interface/theme', theme)
        self.user_settings.set('notifications/enable', notifications_enabled)
        self.user_settings.set('notifications/timeout_seconds', notifications_timeout)

        try:
            self.user_settings.update()
        except Exception as exc:
            logger.warning('Не удалось обновить кеш настроек: %s', exc)

        if self.parent_window and hasattr(self.parent_window, 'apply_user_preferences'):
            try:
                self.parent_window.apply_user_preferences()
            except Exception:
                logger.exception('Ошибка при применении настроек к окну.')

        self._set_apply_enabled(False)

    # overrides
    def apply_changes(self) -> None:
        if not self._dirty and not self._loading:
            return
        self._save_settings()

    def accept(self) -> None:
        if self._dirty:
            self._save_settings()
        super().accept()
