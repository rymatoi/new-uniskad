from __future__ import annotations

from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QCheckBox, QFormLayout, QSpinBox, QVBoxLayout, QWidget

import config.config
from app import app_logger

logger = app_logger.get_logger(__name__)


class GeneralTab(QWidget):
    """Вкладка с общими настройками приложения."""

    def __init__(self, index, parent, main_window=None):
        super().__init__(parent)
        self.index = index
        self.tree_view = parent
        self.mw = main_window

        self._init_ui()
        self._init_values()
        self._create_connections()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.auto_close_checkbox = QCheckBox('Закрывать приложение при бездействии', self)

        self.close_timeout_spinbox = QSpinBox(self)
        self.close_timeout_spinbox.setRange(1, 240)
        self.close_timeout_spinbox.setValue(30)
        self.close_timeout_spinbox.setAccelerated(True)

        self.notification_timeout_spinbox = QSpinBox(self)
        self.notification_timeout_spinbox.setRange(1, 300)
        self.notification_timeout_spinbox.setValue(10)
        self.notification_timeout_spinbox.setAccelerated(True)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.addRow('Таймаут бездействия, мин:', self.close_timeout_spinbox)
        form_layout.addRow('Отображение уведомлений, сек:', self.notification_timeout_spinbox)

        layout.addWidget(self.auto_close_checkbox)
        layout.addLayout(form_layout)
        layout.addStretch()

    def _init_values(self) -> None:
        if self.mw is None:
            return

        auto_close_enabled = self._to_bool(self.mw.user_settings.get('application_close_enabled', True))
        self.auto_close_checkbox.setChecked(auto_close_enabled)

        close_timeout = self._to_int(self.mw.user_settings.get('application_close_timeout', 30), default=30)
        self.close_timeout_spinbox.setValue(max(close_timeout, 1))

        notifications_timeout = self._to_int(self.mw.user_settings.get('notifications_timeout', 10), default=10)
        self.notification_timeout_spinbox.setValue(max(notifications_timeout, 1))

        self._update_timeout_controls(auto_close_enabled)

    def _create_connections(self) -> None:
        self.auto_close_checkbox.toggled.connect(self._on_auto_close_toggled)
        self.close_timeout_spinbox.valueChanged.connect(self._on_close_timeout_changed)
        self.notification_timeout_spinbox.valueChanged.connect(self._on_notification_timeout_changed)

    def _on_auto_close_toggled(self, checked: bool) -> None:
        if self.mw is None:
            return
        self._update_timeout_controls(checked)
        self.mw.user_settings.set('application_close_enabled', checked)
        if checked:
            timeout = self.close_timeout_spinbox.value()
            self.mw.user_settings.set('application_close_timeout', timeout)
            config.config.app.enable_timer(timeout)
        else:
            config.config.app.disable_timer()

    def _on_close_timeout_changed(self, value: int) -> None:
        if self.mw is None or not self.auto_close_checkbox.isChecked():
            return
        self.mw.user_settings.set('application_close_timeout', value)
        config.config.app.enable_timer(value)

    def _on_notification_timeout_changed(self, value: int) -> None:
        if self.mw is None:
            return
        self.mw.user_settings.set('notifications_timeout', value)
        try:
            timeout_ms = int(value) * 1000
        except (TypeError, ValueError):
            logger.exception('Некорректное значение тайм-аута уведомлений: %s', value)
            timeout_ms = 10000
        self.mw.notifications_timeout = timeout_ms

    def _update_timeout_controls(self, enabled: bool) -> None:
        self.close_timeout_spinbox.setEnabled(enabled)

    @staticmethod
    def _to_bool(value: Optional[object]) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {'1', 'true', 't', 'yes', 'y'}
        return bool(value)

    @staticmethod
    def _to_int(value: Optional[object], default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
