from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from db.user_settings import UserSettings
from dialogs.base import BaseDialog


class SettingsDialog(BaseDialog):
    """Локальное окно настроек приложения."""

    settings_applied = Signal(dict)

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)

        self.user_settings = getattr(parent, "user_settings", UserSettings())
        self._defaults = {
            "application_close_timeout": 30,
            "restore_window_layout": True,
            "remember_last_session": True,
            "restore_last_project": True,
            "show_status_bar": True,
            "use_custom_font": False,
            "font_name": QFontDatabase.systemFont(QFontDatabase.GeneralFont).family(),
            "font_size": 10,
            "enable_notifications": True,
            "notifications_timeout": 10,
        }

        self.setWindowTitle("Настройки")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)

        self._dirty = False

        self._build_ui()
        self._load_settings()
        self._connect_signals()

    # UI -----------------------------------------------------------------
    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        self.general_tab = QWidget(self)
        self.appearance_tab = QWidget(self)
        self.data_tab = QWidget(self)

        self.tab_widget.addTab(self.general_tab, "Общие")
        self.tab_widget.addTab(self.appearance_tab, "Интерфейс")
        self.tab_widget.addTab(self.data_tab, "Данные")

        self._init_general_tab()
        self._init_appearance_tab()
        self._init_data_tab()

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply,
            Qt.Horizontal,
            self,
        )
        main_layout.addWidget(self.button_box)

        self.apply_button = self.button_box.button(QDialogButtonBox.Apply)
        if self.apply_button:
            self.apply_button.setEnabled(False)

    def _init_general_tab(self) -> None:
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.close_timeout_spin = QSpinBox(self.general_tab)
        self.close_timeout_spin.setRange(1, 360)
        self.close_timeout_spin.setSuffix(" мин")
        layout.addRow("Авто-выход при простое:", self.close_timeout_spin)

        self.restore_layout_checkbox = QCheckBox("Восстанавливать расположение окон", self.general_tab)
        layout.addRow("", self.restore_layout_checkbox)

        self.remember_session_checkbox = QCheckBox(
            "Запоминать активные панели и раскладки", self.general_tab
        )
        layout.addRow("", self.remember_session_checkbox)

        self.restore_project_checkbox = QCheckBox(
            "Открывать последний проект при запуске", self.general_tab
        )
        layout.addRow("", self.restore_project_checkbox)

        self.status_bar_checkbox = QCheckBox("Показывать строку состояния", self.general_tab)
        layout.addRow("", self.status_bar_checkbox)

        session_group = QGroupBox("Сеанс", self.general_tab)
        session_group.setLayout(layout)

        notifications_layout = QFormLayout()
        notifications_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.notifications_enabled_checkbox = QCheckBox(
            "Показывать всплывающие уведомления", self.general_tab
        )
        notifications_layout.addRow("", self.notifications_enabled_checkbox)

        self.notifications_timeout_spin = QSpinBox(self.general_tab)
        self.notifications_timeout_spin.setRange(1, 120)
        self.notifications_timeout_spin.setSuffix(" сек")
        notifications_layout.addRow("Время отображения:", self.notifications_timeout_spin)

        notifications_group = QGroupBox("Уведомления", self.general_tab)
        notifications_group.setLayout(notifications_layout)

        container_layout = QVBoxLayout(self.general_tab)
        container_layout.addWidget(session_group)
        container_layout.addWidget(notifications_group)
        container_layout.addStretch()

    def _init_appearance_tab(self) -> None:
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.use_custom_font_checkbox = QCheckBox("Использовать собственный шрифт", self.appearance_tab)
        layout.addRow("", self.use_custom_font_checkbox)

        self.font_combo = QFontComboBox(self.appearance_tab)
        layout.addRow("Шрифт интерфейса:", self.font_combo)

        self.font_size_spin = QSpinBox(self.appearance_tab)
        self.font_size_spin.setRange(8, 32)
        layout.addRow("Размер шрифта:", self.font_size_spin)

        group = QGroupBox("Оформление", self.appearance_tab)
        group.setLayout(layout)

        container_layout = QVBoxLayout(self.appearance_tab)
        container_layout.addWidget(group)
        container_layout.addStretch()

    def _init_data_tab(self) -> None:
        container_layout = QVBoxLayout(self.data_tab)

        group = QGroupBox("Управление данными", self.data_tab)
        form = QFormLayout()

        self.clear_session_button = QPushButton("Очистить сохранённую сессию", group)
        form.addRow("", self.clear_session_button)

        self.clear_font_button = QPushButton("Сбросить настройки интерфейса", group)
        form.addRow("", self.clear_font_button)

        group.setLayout(form)
        container_layout.addWidget(group)
        container_layout.addStretch()

    # Settings ------------------------------------------------------------
    def _connect_signals(self) -> None:
        self.button_box.accepted.connect(self._accept)
        self.button_box.rejected.connect(self.reject)
        if self.apply_button:
            self.apply_button.clicked.connect(self._apply)

        # General tab
        self.close_timeout_spin.valueChanged.connect(self._mark_dirty)
        self.restore_layout_checkbox.stateChanged.connect(self._mark_dirty)
        self.remember_session_checkbox.stateChanged.connect(self._mark_dirty)
        self.restore_project_checkbox.stateChanged.connect(self._mark_dirty)
        self.status_bar_checkbox.stateChanged.connect(self._mark_dirty)
        self.notifications_enabled_checkbox.stateChanged.connect(self._mark_dirty)
        self.notifications_timeout_spin.valueChanged.connect(self._mark_dirty)

        # Appearance tab
        self.use_custom_font_checkbox.stateChanged.connect(self._on_use_custom_font_changed)
        self.font_combo.currentFontChanged.connect(lambda *_: self._mark_dirty())
        self.font_size_spin.valueChanged.connect(self._mark_dirty)

        # Data tab
        self.clear_session_button.clicked.connect(self._clear_saved_session)
        self.clear_font_button.clicked.connect(self._clear_interface_settings)

    def _load_settings(self) -> None:
        timeout = int(self._get_setting("application_close_timeout"))
        self.close_timeout_spin.setValue(max(timeout, 1))

        self.restore_layout_checkbox.setChecked(self._get_setting("restore_window_layout"))
        self.remember_session_checkbox.setChecked(self._get_setting("remember_last_session"))
        self.restore_project_checkbox.setChecked(self._get_setting("restore_last_project"))
        self.status_bar_checkbox.setChecked(self._get_setting("show_status_bar"))

        self.notifications_enabled_checkbox.setChecked(
            self._get_setting("enable_notifications")
        )
        timeout_seconds = int(self._get_setting("notifications_timeout"))
        self.notifications_timeout_spin.setValue(max(timeout_seconds, 1))

        self.use_custom_font_checkbox.setChecked(self._get_setting("use_custom_font"))
        current_font = self._get_setting("font_name")
        if current_font:
            self.font_combo.setCurrentFont(QFont(str(current_font)))
        self.font_size_spin.setValue(int(self._get_setting("font_size")))

        self._update_font_controls_state()

    # Helpers -------------------------------------------------------------
    def _get_setting(self, key: str):
        value = self.user_settings.get(key, self._defaults.get(key))
        if isinstance(self._defaults.get(key), bool):
            return self._to_bool(value, self._defaults[key])
        if isinstance(self._defaults.get(key), int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return self._defaults[key]
        return value if value is not None else self._defaults.get(key)

    @staticmethod
    def _to_bool(value, default=False):
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        if isinstance(value, str):
            value = value.strip().lower()
            if value in {"true", "1", "yes", "y", "on"}:
                return True
            if value in {"false", "0", "no", "n", "off"}:
                return False
            return default
        if isinstance(value, (int, float)):
            return value != 0
        return default

    def _mark_dirty(self) -> None:
        self._dirty = True
        if self.apply_button:
            self.apply_button.setEnabled(True)

    def _update_font_controls_state(self) -> None:
        enabled = self.use_custom_font_checkbox.isChecked()
        self.font_combo.setEnabled(enabled)
        self.font_size_spin.setEnabled(enabled)

    def _on_use_custom_font_changed(self):
        self._update_font_controls_state()
        self._mark_dirty()

    def _collect_settings(self) -> Dict[str, object]:
        return {
            "application_close_timeout": int(self.close_timeout_spin.value()),
            "restore_window_layout": self.restore_layout_checkbox.isChecked(),
            "remember_last_session": self.remember_session_checkbox.isChecked(),
            "restore_last_project": self.restore_project_checkbox.isChecked(),
            "show_status_bar": self.status_bar_checkbox.isChecked(),
            "enable_notifications": self.notifications_enabled_checkbox.isChecked(),
            "notifications_timeout": int(self.notifications_timeout_spin.value()),
            "use_custom_font": self.use_custom_font_checkbox.isChecked(),
            "font_name": self.font_combo.currentText(),
            "font_size": int(self.font_size_spin.value()),
        }

    def _apply(self) -> None:
        if not self._dirty:
            return

        values = self._collect_settings()
        for key, value in values.items():
            self.user_settings.set(key, value)

        self.settings_applied.emit(values)

        self._dirty = False
        if self.apply_button:
            self.apply_button.setEnabled(False)

    def _accept(self) -> None:
        self._apply()
        super().accept()

    # Cleanup -------------------------------------------------------------
    def _clear_saved_session(self) -> None:
        keys = [
            "main_window_geometry",
            "main_window_state",
            "central_window_state",
            "tree_states",
            "active_plugins",
            "active_project",
        ]
        for key in keys:
            self.user_settings.remove(key)

        QMessageBox.information(
            self,
            "Сеанс очищен",
            "Сохранённые данные текущего сеанса удалены.",
        )

    def _clear_interface_settings(self) -> None:
        keys = [
            "use_custom_font",
            "font_name",
            "font_size",
        ]
        for key in keys:
            self.user_settings.remove(key)

        general_snapshot = {
            "application_close_timeout": self.close_timeout_spin.value(),
            "restore_window_layout": self.restore_layout_checkbox.isChecked(),
            "remember_last_session": self.remember_session_checkbox.isChecked(),
            "restore_last_project": self.restore_project_checkbox.isChecked(),
            "show_status_bar": self.status_bar_checkbox.isChecked(),
        }

        self._load_settings()

        self.close_timeout_spin.setValue(int(general_snapshot["application_close_timeout"]))
        self.restore_layout_checkbox.setChecked(general_snapshot["restore_window_layout"])
        self.remember_session_checkbox.setChecked(general_snapshot["remember_last_session"])
        self.restore_project_checkbox.setChecked(general_snapshot["restore_last_project"])
        self.status_bar_checkbox.setChecked(general_snapshot["show_status_bar"])
        self._dirty = False
        if self.apply_button:
            self.apply_button.setEnabled(False)

        self.settings_applied.emit({})

        QMessageBox.information(
            self,
            "Интерфейс сброшен",
            "Настройки интерфейса будут восстановлены при следующем запуске.",
        )


__all__ = ["SettingsDialog"]

