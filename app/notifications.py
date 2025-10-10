from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from PySide2.QtCore import Qt, QTimer, Signal
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class NotificationLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

    @classmethod
    def from_value(cls, value: Optional["NotificationLevel | str"]) -> "NotificationLevel":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            normalized = value.lower().strip()
            for member in cls:
                if member.value == normalized:
                    return member
        return cls.INFO


_LEVEL_ACCENT = {
    NotificationLevel.INFO: "#4FC3F7",
    NotificationLevel.SUCCESS: "#4CAF50",
    NotificationLevel.WARNING: "#FFC107",
    NotificationLevel.ERROR: "#F44336",
}


@dataclass
class _ToastMetrics:
    margin: int = 24
    spacing: int = 12


class ToastWidget(QWidget):
    closed = Signal(QWidget)

    def __init__(
        self,
        title: str,
        *,
        message: Optional[str] = None,
        details: Optional[str] = None,
        level: NotificationLevel = NotificationLevel.INFO,
        timeout: Optional[int] = 6000,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            parent,
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._manager: Optional["ToastManager"] = None
        self._timer: Optional[QTimer] = None
        self._details_visible = False
        self._timeout = timeout
        self._level = level

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._frame = QFrame(self)
        self._frame.setObjectName("toastFrame")
        self._frame.setStyleSheet(
            """
            #toastFrame {
                background-color: rgba(43, 45, 48, 235);
                color: #f5f5f5;
                border-radius: 10px;
            }
            QLabel {
                color: #f5f5f5;
            }
            QPushButton {
                border: none;
                padding: 4px 8px;
                border-radius: 6px;
                color: #e0e0e0;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 25);
            }
            QPushButton:checked {
                background: rgba(255, 255, 255, 45);
            }
            QProgressBar {
                border: none;
                border-radius: 6px;
                background: rgba(255, 255, 255, 45);
                height: 8px;
                text-visible: false;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background-color: #4FC3F7;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self._frame.setGraphicsEffect(shadow)

        outer_layout.addWidget(self._frame)

        frame_layout = QHBoxLayout(self._frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        self._accent = QFrame(self._frame)
        self._accent.setFixedWidth(4)
        self._accent.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        frame_layout.addWidget(self._accent)

        self._content_widget = QWidget(self._frame)
        frame_layout.addWidget(self._content_widget)

        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(16, 14, 16, 14)
        content_layout.setSpacing(8)
        self._content_layout = content_layout

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        self._header_layout = header_layout

        self._title_label = QLabel(title, self._content_widget)
        self._title_label.setWordWrap(True)
        header_layout.addWidget(self._title_label, 1)

        self._details_button: Optional[QPushButton] = None
        if details:
            self._details_button = QPushButton("Подробнее", self._content_widget)
            self._details_button.setCheckable(True)
            self._details_button.toggled.connect(self._toggle_details)
            header_layout.addWidget(self._details_button, 0, Qt.AlignTop)

        self._close_button = QPushButton("✕", self._content_widget)
        self._close_button.setFixedSize(24, 24)
        self._close_button.clicked.connect(self.close)
        header_layout.addWidget(self._close_button, 0, Qt.AlignTop)

        content_layout.addLayout(header_layout)

        self._message_label: Optional[QLabel] = None
        if message:
            self._message_label = QLabel(message, self._content_widget)
            self._message_label.setWordWrap(True)
            self._message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            content_layout.addWidget(self._message_label)

        self._details_label: Optional[QLabel] = None
        if details:
            self._details_label = QLabel(details, self._content_widget)
            self._details_label.setWordWrap(True)
            self._details_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._details_label.setVisible(False)
            content_layout.addWidget(self._details_label)

        self._progress_bar: Optional[QProgressBar] = None

        self._apply_level(level)

        if timeout:
            self._start_timer(timeout)

    def _start_timer(self, timeout: int) -> None:
        if self._timer is not None:
            self._timer.stop()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)
        self._timer.start(timeout)

    def set_manager(self, manager: "ToastManager") -> None:
        self._manager = manager

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)
        self._adjust_and_reposition()

    def set_message(self, message: Optional[str]) -> None:
        if message:
            if self._message_label is None:
                self._message_label = QLabel(message, self._content_widget)
                self._message_label.setWordWrap(True)
                self._message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                self._content_layout.insertWidget(1, self._message_label)
            else:
                self._message_label.setText(message)
        elif self._message_label is not None:
            self._message_label.setVisible(False)
        self._adjust_and_reposition()

    def set_details(self, details: Optional[str]) -> None:
        if details:
            if self._details_label is None:
                self._details_label = QLabel(details, self._content_widget)
                self._details_label.setWordWrap(True)
                self._details_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                self._details_label.setVisible(self._details_visible)
                self._content_layout.addWidget(self._details_label)
            else:
                self._details_label.setText(details)
            if self._details_button is None:
                self._details_button = QPushButton("Подробнее", self._content_widget)
                self._details_button.setCheckable(True)
                self._details_button.toggled.connect(self._toggle_details)
                self._header_layout.insertWidget(1, self._details_button)
        elif self._details_label is not None:
            self._details_label.hide()
            self._details_label.deleteLater()
            self._details_label = None
            if self._details_button is not None:
                self._header_layout.removeWidget(self._details_button)
                self._details_button.hide()
                self._details_button.deleteLater()
                self._details_button = None
        self._adjust_and_reposition()

    def set_level(self, level: NotificationLevel) -> None:
        self._level = level
        self._apply_level(level)

    def _apply_level(self, level: NotificationLevel) -> None:
        accent_color = _LEVEL_ACCENT.get(level, _LEVEL_ACCENT[NotificationLevel.INFO])
        self._accent.setStyleSheet(f"background-color: {accent_color}; border-top-left-radius: 10px; border-bottom-left-radius: 10px;")
        if self._progress_bar is not None:
            self._progress_bar.setStyleSheet(
                self._frame.styleSheet() + f"\nQProgressBar::chunk {{ background-color: {accent_color}; }}"
            )

    def attach_progress_bar(self) -> QProgressBar:
        if self._progress_bar is None:
            self._progress_bar = QProgressBar(self._content_widget)
            self._progress_bar.setRange(0, 0)
            self._progress_bar.setTextVisible(False)
            self._content_layout.insertWidget(1, self._progress_bar)
            self._apply_level(self._level)
        return self._progress_bar

    def start_auto_close(self, timeout: int) -> None:
        self._timeout = timeout
        self._start_timer(timeout)

    def _toggle_details(self, checked: bool) -> None:
        self._details_visible = checked
        if self._details_label is not None:
            self._details_label.setVisible(checked)
        if self._details_button is not None:
            self._details_button.setText("Скрыть" if checked else "Подробнее")
        self._adjust_and_reposition()

    def _adjust_and_reposition(self) -> None:
        self.adjustSize()
        if self._manager:
            self._manager.reposition()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        super().closeEvent(event)
        self.closed.emit(self)
        QTimer.singleShot(0, self.deleteLater)


class ToastProgress(ToastWidget):
    def __init__(
        self,
        title: str,
        *,
        message: Optional[str] = None,
        details: Optional[str] = None,
        level: NotificationLevel = NotificationLevel.INFO,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(title, message=message, details=details, level=level, timeout=None, parent=parent)
        self.attach_progress_bar()

    def update(self, title: Optional[str] = None, *, message: Optional[str] = None, details: Optional[str] = None) -> None:
        if title:
            self.set_title(title)
        if message is not None:
            self.set_message(message)
        if details is not None:
            self.set_details(details)

    def finish(self, title: Optional[str] = None, *, success: bool = True, timeout: int = 2000) -> None:
        progress_bar = self.attach_progress_bar()
        progress_bar.setRange(0, 1)
        progress_bar.setValue(1)
        self.set_level(NotificationLevel.SUCCESS if success else NotificationLevel.ERROR)
        if title:
            self.set_title(title)
        self.start_auto_close(timeout)


class ToastManager:
    def __init__(self, parent: QWidget) -> None:
        self._parent = parent
        self._toasts: List[ToastWidget] = []
        self._metrics = _ToastMetrics()

    def _register(self, toast: ToastWidget) -> ToastWidget:
        toast.set_manager(self)
        toast.closed.connect(self._on_toast_closed)
        toast.setParent(self._parent)
        toast.show()
        toast.raise_()
        self._toasts.append(toast)
        self.reposition()
        return toast

    def show_toast(
        self,
        title: str,
        *,
        message: Optional[str] = None,
        details: Optional[str] = None,
        level: NotificationLevel = NotificationLevel.INFO,
        timeout: Optional[int] = 6000,
    ) -> ToastWidget:
        toast = ToastWidget(
            title,
            message=message,
            details=details,
            level=level,
            timeout=timeout,
            parent=self._parent,
        )
        return self._register(toast)

    def show_progress(
        self,
        title: str,
        *,
        message: Optional[str] = None,
        details: Optional[str] = None,
        level: NotificationLevel = NotificationLevel.INFO,
    ) -> ToastProgress:
        toast = ToastProgress(
            title,
            message=message,
            details=details,
            level=level,
            parent=self._parent,
        )
        return self._register(toast)

    def _on_toast_closed(self, toast: QWidget) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)  # type: ignore[arg-type]
            self.reposition()

    def reposition(self) -> None:
        if not self._toasts:
            return
        parent_rect = self._parent.geometry()
        bottom = parent_rect.y() + parent_rect.height() - self._metrics.margin
        right = parent_rect.x() + parent_rect.width() - self._metrics.margin
        for toast in reversed(self._toasts):
            toast.adjustSize()
            toast.move(right - toast.width(), bottom - toast.height())
            bottom -= toast.height() + self._metrics.spacing

    def clear(self) -> None:
        for toast in list(self._toasts):
            toast.close()
        self._toasts.clear()


__all__ = [
    "NotificationLevel",
    "ToastManager",
    "ToastProgress",
    "ToastWidget",
]
