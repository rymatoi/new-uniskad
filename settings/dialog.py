from __future__ import annotations

from typing import Dict

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
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
            "color_theme": "system",
            "compact_mode": False,
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

        group = QGroupBox("Сеанс", self.general_tab)
        group.setLayout(layout)

        container_layout = QVBoxLayout(self.general_tab)
        container_layout.addWidget(group)
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

        self.theme_combo = QComboBox(self.appearance_tab)
        self.theme_combo.addItem("Системная тема", "system")
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Тёмная", "dark")
        layout.addRow("Цветовая схема:", self.theme_combo)

        self.compact_mode_checkbox = QCheckBox("Компактный режим элементов", self.appearance_tab)
        layout.addRow("", self.compact_mode_checkbox)

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

        # Appearance tab
        self.use_custom_font_checkbox.stateChanged.connect(self._on_use_custom_font_changed)
        self.font_combo.currentFontChanged.connect(lambda *_: self._mark_dirty())
        self.font_size_spin.valueChanged.connect(self._mark_dirty)
        self.theme_combo.currentIndexChanged.connect(self._mark_dirty)
        self.compact_mode_checkbox.stateChanged.connect(self._mark_dirty)

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

        self.use_custom_font_checkbox.setChecked(self._get_setting("use_custom_font"))
        current_font = self._get_setting("font_name")
        if current_font:
            self.font_combo.setCurrentFont(QFont(str(current_font)))
        self.font_size_spin.setValue(int(self._get_setting("font_size")))

        theme_key = str(self._get_setting("color_theme"))
        index = self.theme_combo.findData(theme_key)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
        else:
            self.theme_combo.setCurrentIndex(0)

        self.compact_mode_checkbox.setChecked(self._get_setting("compact_mode"))

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
            "use_custom_font": self.use_custom_font_checkbox.isChecked(),
            "font_name": self.font_combo.currentText(),
            "font_size": int(self.font_size_spin.value()),
            "color_theme": self.theme_combo.currentData(),
            "compact_mode": self.compact_mode_checkbox.isChecked(),
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
            "color_theme",
            "compact_mode",
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

