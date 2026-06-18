from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from PySide2.QtCore import QTimer, Qt, Signal
from PySide2.QtGui import QColor, QFont
from PySide2.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QStyle,
    QProgressBar,
)


class ToastLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"


_LEVEL_STYLES = {
    ToastLevel.INFO: {
        "accent": "#4C8BF5",
        "icon": "\u2139",
    },
    ToastLevel.SUCCESS: {
        "accent": "#2DBE6C",
        "icon": "\u2714",
    },
    ToastLevel.WARNING: {
        "accent": "#F2C94C",
        "icon": "\u26A0",
    },
    ToastLevel.ERROR: {
        "accent": "#EB5757",
        "icon": "\u2716",
    },
    ToastLevel.PROGRESS: {
        "accent": "#56CCF2",
        "icon": "\u23F3",
    },
}


class ToastNotification(QFrame):
    closed = Signal(object)

    def __init__(
        self,
        message: str,
        *,
        level: Union[ToastLevel, str] = ToastLevel.INFO,
        timeout: Optional[int] = 6000,
        details: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("toastNotification")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._level = self._normalize_level(level)
        self._message = message
        self._details = details
        self._timeout = timeout

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)

        self._build_ui()
        self.set_message(message)
        if details:
            self.set_details(details)

        self._apply_level_style()

        if timeout and timeout > 0:
            self._timer.start(timeout)

    @staticmethod
    def _normalize_level(level: Union[ToastLevel, str]) -> ToastLevel:
        if isinstance(level, ToastLevel):
            return level
        try:
            return ToastLevel(level.lower())
        except Exception:
            return ToastLevel.INFO

    def _build_ui(self) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 6)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.icon_label = QLabel(self)
        self.icon_label.setObjectName("toastIcon")
        self.icon_label.setMinimumWidth(22)
        icon_font = QFont()
        icon_font.setPointSize(14)
        self.icon_label.setFont(icon_font)
        header_layout.addWidget(self.icon_label, 0, Qt.AlignTop)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(6)

        self.message_label = QLabel(self)
        self.message_label.setObjectName("toastMessage")
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_layout.addWidget(self.message_label)

        self.details_button = QPushButton("Подробнее", self)
        self.details_button.setObjectName("toastDetailsButton")
        self.details_button.setCheckable(True)
        self.details_button.toggled.connect(self._toggle_details)
        self.details_button.hide()
        title_layout.addWidget(self.details_button, 0, Qt.AlignLeft)

        header_layout.addLayout(title_layout)

        self.close_button = QToolButton(self)
        self.close_button.setObjectName("toastCloseButton")
        self.close_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.close)
        header_layout.addWidget(self.close_button, 0, Qt.AlignTop)

        layout.addLayout(header_layout)

        self._body_layout = QVBoxLayout()
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(8)
        layout.addLayout(self._body_layout)

        self.details_panel = QTextEdit(self)
        self.details_panel.setObjectName("toastDetails")
        self.details_panel.setReadOnly(True)
        self.details_panel.setVisible(False)
        self.details_panel.setFrameShape(QFrame.NoFrame)
        self.details_panel.setMinimumHeight(96)
        self.details_panel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.details_panel)

    def _apply_level_style(self) -> None:
        style = _LEVEL_STYLES.get(self._level, _LEVEL_STYLES[ToastLevel.INFO])
        accent = style["accent"]

        stylesheet = f"""
        #toastNotification {{
            background-color: rgba(34, 37, 42, 230);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        #toastIcon {{
            color: {accent};
        }}
        #toastMessage {{
            color: #ECEFF4;
            font-size: 13px;
        }}
        #toastCloseButton {{
            border: none;
            padding: 4px;
            color: rgba(255, 255, 255, 0.6);
        }}
        #toastCloseButton:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            color: rgba(255, 255, 255, 0.85);
        }}
        #toastDetailsButton {{
            background: transparent;
            color: {accent};
            border: none;
            padding: 0px;
            font-size: 12px;
        }}
        #toastDetailsButton:checked {{
            color: rgba(255, 255, 255, 0.9);
        }}
        #toastDetails {{
            background: rgba(255, 255, 255, 0.04);
            color: rgba(255, 255, 255, 0.85);
            border-radius: 8px;
            padding: 10px;
            font-size: 12px;
        }}
        """

        self.setStyleSheet(stylesheet)
        self.icon_label.setText(style["icon"])

    def add_body_widget(self, widget: QWidget) -> None:
        self._body_layout.addWidget(widget)

    def set_message(self, message: str) -> None:
        self._message = message
        self.message_label.setText(message)

    def set_details(self, details: Optional[str]) -> None:
        self._details = details
        if details:
            self.details_panel.setText(details)
            self.details_panel.show()
            self.details_panel.setVisible(self.details_button.isChecked())
            self.details_button.show()
        else:
            self.details_panel.hide()
            self.details_button.hide()

    def update_level(self, level: Union[ToastLevel, str]) -> None:
        new_level = self._normalize_level(level)
        if new_level == self._level:
            return
        self._level = new_level
        self._apply_level_style()

    def pause_timeout(self) -> None:
        if self._timer.isActive():
            self._timer.stop()

    def resume_timeout(self) -> None:
        if self._timeout and self._timeout > 0:
            self._timer.start(self._timeout)

    def start_auto_close(self, timeout: Optional[int] = None) -> None:
        if timeout is not None:
            self._timeout = timeout
        if self._timeout and self._timeout > 0:
            self._timer.start(self._timeout)
        else:
            self._timer.stop()

    def _toggle_details(self, state: bool) -> None:
        if self._details:
            self.details_panel.setVisible(state)

    def enterEvent(self, event) -> None:  # noqa: D401 - Qt override
        self.pause_timeout()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: D401 - Qt override
        self.resume_timeout()
        super().leaveEvent(event)

    def closeEvent(self, event) -> None:  # noqa: D401 - Qt override
        self.closed.emit(self)
        super().closeEvent(event)


class ProgressToastNotification(ToastNotification):
    def __init__(
        self,
        message: str,
        *,
        details: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            message,
            level=ToastLevel.PROGRESS,
            timeout=None,
            details=details,
            parent=parent,
        )

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("toastProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setRange(0, 0)
        self.add_body_widget(self.progress_bar)

        self.setStyleSheet(self.styleSheet() + "\n"
                           "#toastProgress {"
                           "    background: rgba(255, 255, 255, 0.07);"
                           "    border-radius: 4px;"
                           "}"
                           "#toastProgress::chunk {"
                           "    background: #56CCF2;"
                           "    border-radius: 4px;"
                           "}")

    def update_progress(
        self,
        *,
        message: Optional[str] = None,
        details: Optional[str] = None,
        value: Optional[int] = None,
        maximum: Optional[int] = None,
    ) -> None:
        if message is not None:
            self.set_message(message)
        if details is not None:
            self.set_details(details)
        if value is None or maximum is None:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(max(0, min(value, maximum)))

    def complete(self, message: Optional[str] = None, timeout: int = 2000) -> None:
        if message:
            self.set_message(message)
        self.update_level(ToastLevel.SUCCESS)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.start_auto_close(timeout)

    def fail(self, message: Optional[str] = None, details: Optional[str] = None) -> None:
        if message:
            self.set_message(message)
        if details is not None:
            self.set_details(details)
        self.update_level(ToastLevel.ERROR)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.start_auto_close(None)


class NotificationCenter(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, max_visible: int = 5) -> None:
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)

        self._max_visible = max_visible
        self._notifications: List[ToastNotification] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self._layout = layout

        self.hide()

    def _install_toast(self, toast: ToastNotification) -> ToastNotification:
        if len(self._notifications) >= self._max_visible:
            self._notifications[0].close()

        toast.setParent(self)
        toast.closed.connect(self._handle_closed)
        self._layout.addWidget(toast, 0, Qt.AlignRight)
        self._notifications.append(toast)
        toast.show()
        self._update_geometry()
        return toast

    def show_message(
        self,
        message: str,
        *,
        level: Union[ToastLevel, str] = ToastLevel.INFO,
        timeout: Optional[int] = 6000,
        details: Optional[str] = None,
    ) -> ToastNotification:
        toast = ToastNotification(message, level=level, timeout=timeout, details=details)
        return self._install_toast(toast)

    def show_progress(
        self,
        message: str,
        *,
        details: Optional[str] = None,
    ) -> ProgressToastNotification:
        toast = ProgressToastNotification(message, details=details)
        return self._install_toast(toast)

    def clear(self) -> None:
        for toast in list(self._notifications):
            toast.close()

    def _handle_closed(self, toast: ToastNotification) -> None:
        if toast in self._notifications:
            self._notifications.remove(toast)
        self._layout.removeWidget(toast)
        toast.deleteLater()
        self._update_geometry()

    def _update_geometry(self) -> None:
        if not self._notifications:
            self.hide()
            return

        self.adjustSize()
        parent = self.parentWidget()
        if parent:
            parent_geometry = parent.frameGeometry()
            x = parent_geometry.right() - self.width() - 24
            y = parent_geometry.bottom() - self.height() - 24
            self.move(x, y)
        self.show()

    def reposition(self) -> None:
        if not self._notifications:
            return
        self._update_geometry()

    def hide_all(self) -> None:
        self.clear()
        self.hide()
