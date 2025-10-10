from __future__ import annotations

from dataclasses import dataclass

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from dialogs.base import BaseDialog
from db.user_settings import UserSettings


@dataclass
class SettingsValues:
    auto_close_enabled: bool
    auto_close_timeout: int
    remember_window_state: bool
    always_on_top: bool
    show_progress_bar: bool
    notifications_timeout: int

    @classmethod
    def from_storage(cls, storage: UserSettings) -> "SettingsValues":
        return cls(
            auto_close_enabled=bool(storage.get('auto_close_enabled', True)),
            auto_close_timeout=int(storage.get('application_close_timeout', 30) or 0),
            remember_window_state=bool(storage.get('remember_window_state', True)),
            always_on_top=bool(storage.get('main_window_always_on_top', False)),
            show_progress_bar=bool(storage.get('show_progress_bar', True)),
            notifications_timeout=int(storage.get('notifications_timeout', 10000) or 0),
        )


class SettingsDialog(BaseDialog):
    """Диалог локальных настроек приложения."""

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.setWindowTitle('Настройки')
        self.resize(520, 360)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)

        self._main_window = parent if parent and hasattr(parent, 'user_settings') else None
        self._settings: UserSettings = (
            parent.user_settings if self._main_window is not None else UserSettings()
        )

        self.values = SettingsValues.from_storage(self._settings)

        self._init_ui()
        self._load_values()
        self._create_connections()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # General tab
        general_tab = QWidget(self)
        general_layout = QFormLayout(general_tab)

        self.auto_close_checkbox = QCheckBox('Включить авто-закрытие при бездействии', general_tab)
        self.auto_close_timeout_spin = QSpinBox(general_tab)
        self.auto_close_timeout_spin.setMinimum(1)
        self.auto_close_timeout_spin.setMaximum(240)
        self.auto_close_timeout_spin.setSuffix(' мин')
        self.auto_close_timeout_spin.setToolTip('Количество минут до автоматического закрытия приложения')

        self.remember_state_checkbox = QCheckBox('Запоминать расположение окон и панелей', general_tab)

        general_layout.addRow(self.auto_close_checkbox)
        general_layout.addRow('Таймер бездействия:', self.auto_close_timeout_spin)
        general_layout.addRow(self.remember_state_checkbox)

        self.tabs.addTab(general_tab, 'Общие')

        # Interface tab
        interface_tab = QWidget(self)
        interface_layout = QFormLayout(interface_tab)

        self.always_on_top_checkbox = QCheckBox('Держать главное окно поверх других', interface_tab)
        self.show_progress_bar_checkbox = QCheckBox('Показывать индикатор прогресса', interface_tab)

        timeout_layout = QHBoxLayout()
        self.notifications_timeout_spin = QSpinBox(interface_tab)
        self.notifications_timeout_spin.setMinimum(1)
        self.notifications_timeout_spin.setMaximum(300)
        self.notifications_timeout_spin.setSuffix(' с')
        timeout_layout.addWidget(self.notifications_timeout_spin)
        timeout_layout.addWidget(QLabel('время показа уведомлений', interface_tab))

        notifications_container = QWidget(interface_tab)
        notifications_container.setLayout(timeout_layout)

        interface_layout.addRow(self.always_on_top_checkbox)
        interface_layout.addRow(self.show_progress_bar_checkbox)
        interface_layout.addRow('Уведомления:', notifications_container)

        self.tabs.addTab(interface_tab, 'Интерфейс')

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply,
            Qt.Horizontal,
            self,
        )
        layout.addWidget(self.button_box)

    def _load_values(self) -> None:
        self.auto_close_checkbox.setChecked(self.values.auto_close_enabled)
        self.auto_close_timeout_spin.setValue(max(self.values.auto_close_timeout, 1))
        self.auto_close_timeout_spin.setEnabled(self.values.auto_close_enabled)

        self.remember_state_checkbox.setChecked(self.values.remember_window_state)

        self.always_on_top_checkbox.setChecked(self.values.always_on_top)
        self.show_progress_bar_checkbox.setChecked(self.values.show_progress_bar)

        timeout_seconds = max(int(self.values.notifications_timeout / 1000), 1)
        self.notifications_timeout_spin.setValue(timeout_seconds)

    def _create_connections(self) -> None:
        self.auto_close_checkbox.toggled.connect(self.auto_close_timeout_spin.setEnabled)
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        if apply_button is not None:
            apply_button.clicked.connect(self.apply)

    def _collect_values(self) -> SettingsValues:
        auto_close_enabled = self.auto_close_checkbox.isChecked()
        timeout_value = self.auto_close_timeout_spin.value() if auto_close_enabled else 0
        notifications_timeout_ms = self.notifications_timeout_spin.value() * 1000

        return SettingsValues(
            auto_close_enabled=auto_close_enabled,
            auto_close_timeout=timeout_value,
            remember_window_state=self.remember_state_checkbox.isChecked(),
            always_on_top=self.always_on_top_checkbox.isChecked(),
            show_progress_bar=self.show_progress_bar_checkbox.isChecked(),
            notifications_timeout=notifications_timeout_ms,
        )

    def _store_values(self, values: SettingsValues) -> None:
        self._settings.set('auto_close_enabled', values.auto_close_enabled)
        self._settings.set('application_close_timeout', values.auto_close_timeout or 0)
        self._settings.set('remember_window_state', values.remember_window_state)
        self._settings.set('main_window_always_on_top', values.always_on_top)
        self._settings.set('show_progress_bar', values.show_progress_bar)
        self._settings.set('notifications_timeout', values.notifications_timeout)

        if not values.remember_window_state:
            for key in (
                'main_window_geometry',
                'main_window_state',
                'central_window_state',
                'tree_states',
                'active_plugins',
                'active_project',
            ):
                self._settings.remove(key)

    def apply(self) -> None:
        self.values = self._collect_values()
        self._store_values(self.values)
        if self._main_window and hasattr(self._main_window, 'apply_settings_from_storage'):
            self._main_window.apply_settings_from_storage()

    def _on_accept(self) -> None:
        self.apply()
        self.accept()
