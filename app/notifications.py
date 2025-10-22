from __future__ import annotations

from typing import Optional

from PySide2.QtCore import QPoint, Qt, QTimer, Signal
from PySide2.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)


class Notification(QWidget):
    """Single toast notification with optional progress indicator and details."""

    closed = Signal(QWidget)
    minimize_requested = Signal(QWidget)
    details_toggled = Signal(bool)

    VARIANT_STYLES = {
        "info": ("#3c3f41", "#2c2f30"),
        "success": ("#2f5d3a", "#1e4027"),
        "warning": ("#5d4a2f", "#3e311f"),
        "error": ("#5d2f2f", "#3d1f1f"),
        "progress": ("#2f405d", "#1f2c3d"),
    }

    def __init__(
        self,
        message: str,
        *,
        timeout: Optional[int] = 5000,
        parent: Optional[QWidget] = None,
        details: Optional[str] = None,
        variant: str = "info",
        show_progress: bool = False,
    ) -> None:
        super().__init__(parent)

        self._timeout = timeout
        self._variant = variant if variant in self.VARIANT_STYLES else "info"
        self._progress_active = show_progress
        self.is_progress_toast = show_progress

        self._detail_lines: list[str] = []
        if details:
            if isinstance(details, str):
                self._detail_lines = [details]
            else:
                self._detail_lines = list(details)
        self._details_text = "\n".join(self._detail_lines)

        self.setAttribute(Qt.WA_StyledBackground, True)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.frame = QFrame(self)
        self.frame.setObjectName("notificationFrame")
        outer_layout.addWidget(self.frame)

        self.layout = QVBoxLayout(self.frame)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = QLabel(message, self.frame)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #f1f1f1; font-weight: 600;")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        header_layout.addWidget(self.title_label)

        self.progress_bar: Optional[QProgressBar]
        if show_progress:
            self.progress_bar = QProgressBar(self.frame)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setFixedHeight(4)
            self.progress_bar.setStyleSheet(
                "QProgressBar {"
                "background-color: rgba(255, 255, 255, 0.15);"
                "border-radius: 2px;"
                "}"
                "QProgressBar::chunk {"
                "background-color: #62a0ff;"
                "border-radius: 2px;"
                "}"
            )
        else:
            self.progress_bar = None

        self.detail_toggle = QToolButton(self.frame)
        self.detail_toggle.setCheckable(True)
        self.detail_toggle.setArrowType(Qt.RightArrow)
        self.detail_toggle.setStyleSheet(
            "QToolButton {"
            "border: none;"
            "color: #f1f1f1;"
            "padding: 2px;"
            "}"
            "QToolButton::checked { color: #f1f1f1; }"
        )
        self.detail_toggle.setVisible(bool(self._detail_lines))
        self.detail_toggle.toggled.connect(self._toggle_details)
        header_layout.addWidget(self.detail_toggle, 0, Qt.AlignRight)

        self.minimize_button = QToolButton(self.frame)
        self.minimize_button.setText("⤓")
        self.minimize_button.setToolTip("Свернуть в статус-бар")
        self.minimize_button.setStyleSheet(
            "QToolButton {"
            "border: none;"
            "color: #f1f1f1;"
            "padding: 2px;"
            "}"
            "QToolButton::hover { color: #ffffff; }"
        )
        self.minimize_button.clicked.connect(lambda: self.minimize_requested.emit(self))
        self.minimize_button.setVisible(show_progress)
        header_layout.addWidget(self.minimize_button, 0, Qt.AlignRight)

        self.close_button = QPushButton("✕", self.frame)
        self.close_button.setFixedSize(22, 22)
        self.close_button.setStyleSheet(
            "QPushButton {"
            "color: #f1f1f1;"
            "font-weight: bold;"
            "background-color: rgba(255, 255, 255, 0.08);"
            "border: none;"
            "border-radius: 11px;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(255, 255, 255, 0.18);"
            "}"
        )
        self.close_button.clicked.connect(self.dismiss)
        header_layout.addWidget(self.close_button, 0, Qt.AlignRight)

        self.layout.addLayout(header_layout)

        if self.progress_bar is not None:
            self.layout.addWidget(self.progress_bar)

        self.details_label = QLabel(self._details_text, self.frame)
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #d0d0d0; line-height: 1.4;")
        self.details_label.setVisible(False)
        self.layout.addWidget(self.details_label)

        self._timer: Optional[QTimer] = None
        if timeout and timeout > 0:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.dismiss)
            self._timer.start(timeout)

        self.set_variant(self._variant)

    def request_relayout(self) -> None:
        parent = self.parent()
        if isinstance(parent, StackedNotifications):
            parent.request_relayout()

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANT_STYLES:
            variant = "info"
        self._variant = variant
        background, border = self.VARIANT_STYLES[variant]
        self.frame.setStyleSheet(
            "QFrame#notificationFrame {"
            f"background-color: {background};"
            f"border: 1px solid {border};"
            "border-radius: 10px;"
            "}"
        )
        self.minimize_button.setVisible(self.is_progress_toast and variant == "progress")
        if self.progress_bar is not None and variant != "progress":
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(1)

    def restart_timer(self, timeout: Optional[int]) -> None:
        self._timeout = timeout
        if self._timer is not None:
            self._timer.stop()
            self._timer.deleteLater()
            self._timer = None
        if timeout and timeout > 0:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.dismiss)
            self._timer.start(timeout)

    def set_message(self, message: str) -> None:
        self.title_label.setText(message)
        self.request_relayout()

    def set_details(self, details: Optional[str]) -> None:
        if details:
            if isinstance(details, str):
                self._detail_lines = [details]
            else:
                self._detail_lines = list(details)
        else:
            self._detail_lines = []
        self._details_text = "\n".join(self._detail_lines)
        has_details = bool(self._detail_lines)
        self.detail_toggle.setVisible(has_details)
        if has_details and self.detail_toggle.isChecked():
            self.details_label.setText(self._details_text)
            self.details_label.setVisible(True)
        else:
            self.details_label.clear()
            self.details_label.setVisible(False)
            if self.detail_toggle.isChecked():
                self.detail_toggle.setChecked(False)
        self.request_relayout()

    def append_detail(self, detail: str) -> None:
        if not detail:
            return
        self._detail_lines.append(detail)
        self._details_text = "\n".join(self._detail_lines)
        self.detail_toggle.setVisible(True)
        if self.detail_toggle.isChecked():
            self.details_label.setText(self._details_text)
            self.details_label.setVisible(True)
        self.request_relayout()

    def clear_details(self) -> None:
        self._detail_lines.clear()
        self._details_text = ""
        self.details_label.clear()
        self.details_label.setVisible(False)
        self.detail_toggle.blockSignals(True)
        self.detail_toggle.setChecked(False)
        self.detail_toggle.blockSignals(False)
        self.detail_toggle.setVisible(False)
        self.request_relayout()

    def is_details_expanded(self) -> bool:
        return self.detail_toggle.isChecked()

    def mark_complete(self, message: Optional[str] = None, details: Optional[str] = None, auto_close: int = 2500) -> None:
        if message:
            self.set_message(message)
        if details is not None:
            self.set_details(details)
        if self.progress_bar is not None:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(1)
        self.set_variant("success")
        self.restart_timer(auto_close)
        self._progress_active = False
        if self.is_progress_toast:
            self.minimize_button.setVisible(False)

    def mark_failed(self, message: Optional[str] = None, details: Optional[str] = None, auto_close: Optional[int] = None) -> None:
        if message:
            self.set_message(message)
        if details is not None:
            self.set_details(details)
        if self.progress_bar is not None:
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
        self.set_variant("error")
        self.restart_timer(auto_close)
        self._progress_active = False
        if self.is_progress_toast:
            self.minimize_button.setVisible(False)

    def dismiss(self) -> None:
        if self._timer is not None:
            self._timer.stop()
        self.closed.emit(self)

    def _toggle_details(self, checked: bool) -> None:
        self.detail_toggle.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        has_text = bool(self._detail_lines)
        if checked and has_text:
            self.details_label.setText(self._details_text)
        self.details_label.setVisible(checked and has_text)
        self.details_toggled.emit(checked)
        self.request_relayout()


class StackedNotifications(QWidget):
    """Floating widget that stacks toast notifications similar to PyCharm."""

    def __init__(self, parent: Optional[QWidget] = None, max_notifications: int = 10) -> None:
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.max_notifications = max_notifications
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(10)

        self._notifications: list[Notification] = []

    def add_notification(
        self,
        message: str,
        timeout: Optional[int] = 5000,
        *,
        details: Optional[str] = None,
        variant: str = "info",
        show_progress: bool = False,
    ) -> Notification:
        if len(self._notifications) >= self.max_notifications:
            stale = self._notifications.pop(0)
            stale.dismiss()

        notification = Notification(
            message,
            timeout=timeout,
            parent=self,
            details=details,
            variant=variant,
            show_progress=show_progress,
        )
        notification.closed.connect(self.remove_notification)
        self._notifications.append(notification)
        self.layout.addWidget(notification)

        notification.show()
        self.show()
        self.request_relayout()
        return notification

    def remove_notification(self, notification: QWidget) -> None:
        if notification in self._notifications:
            self._notifications.remove(notification)  # type: ignore[arg-type]
        if self.layout.indexOf(notification) != -1:
            self.layout.removeWidget(notification)
        notification.deleteLater()
        if not self._notifications:
            self.hide()
        self.request_relayout()

    def request_relayout(self) -> None:
        self.adjustSize()
        self.update_position()

    def update_position(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        self.move(
            max(0, geometry.right() - self.width() - 24),
            max(0, geometry.bottom() - self.height() - 24),
        )

    def minimize_notification(self, notification: Notification) -> None:
        if notification not in self._notifications:
            return
        if self.layout.indexOf(notification) != -1:
            self.layout.removeWidget(notification)
        notification.hide()
        if not any(n.isVisible() for n in self._notifications):
            self.hide()
        self.request_relayout()

    def restore_notification(self, notification: Notification) -> None:
        if notification not in self._notifications:
            self._notifications.append(notification)
        if self.layout.indexOf(notification) == -1:
            self.layout.addWidget(notification)
        notification.show()
        self.show()
        self.request_relayout()
