from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide2.QtCore import QEvent, QPoint, QRect, Qt, QTimer, Signal, QObject
from PySide2.QtGui import QColor, QFont
from PySide2.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app import app_logger

logger = app_logger.get_logger(__name__)


@dataclass(frozen=True)
class ToastColors:
    background: str
    border: str
    accent: str


LEVEL_COLORS = {
    "info": ToastColors("#2b2d30", "#39404d", "#4fc3f7"),
    "success": ToastColors("#243228", "#2f4f32", "#81c784"),
    "warning": ToastColors("#3b3020", "#5d4024", "#ffb74d"),
    "error": ToastColors("#3a2327", "#552931", "#ef5350"),
}


class _ToastBase(QFrame):
    closed = Signal(object)

    def __init__(
        self,
        title: str,
        message: str,
        level: str = "info",
        *,
        details: Optional[str] = None,
        timeout: Optional[int] = 6000,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("ToastFrame")

        colors = LEVEL_COLORS.get(level, LEVEL_COLORS["info"])
        self._details_visible = False

        self.setStyleSheet(
            """
            #ToastFrame {
                border-radius: 12px;
                border: 1px solid %s;
                background-color: %s;
            }
            QLabel#TitleLabel {
                color: #f1f1f1;
                font-weight: 600;
            }
            QLabel#MessageLabel {
                color: #f1f1f1;
            }
            QTextEdit#DetailsEdit {
                background-color: rgba(0, 0, 0, 0.15);
                border: none;
                border-radius: 8px;
                color: #f1f1f1;
                padding: 6px;
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 11px;
            }
            QPushButton#CloseButton {
                border: none;
                color: #cfd3da;
                padding: 2px 6px;
                font-weight: 600;
                background-color: transparent;
            }
            QPushButton#CloseButton:hover {
                color: #ffffff;
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QPushButton#DetailsButton {
                border: none;
                color: %s;
                padding: 0;
                font-weight: 600;
                background-color: transparent;
            }
            QPushButton#DetailsButton:hover {
                color: #ffffff;
            }
            """
            % (colors.border, colors.background, colors.accent)
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        self._accent = colors.accent
        self._title = QLabel(title)
        self._title.setObjectName("TitleLabel")
        self._title.setFont(QFont(self._title.font().family(), 11))

        self._close_button = QPushButton("✕")
        self._close_button.setObjectName("CloseButton")
        self._close_button.setCursor(Qt.PointingHandCursor)
        self._close_button.clicked.connect(self.close_toast)

        header_layout.addWidget(self._title, 1)
        header_layout.addWidget(self._close_button, 0, Qt.AlignTop)

        self._message_label = QLabel(message)
        self._message_label.setObjectName("MessageLabel")
        self._message_label.setWordWrap(True)

        layout.addLayout(header_layout)
        layout.addWidget(self._message_label)

        self._details_button: Optional[QPushButton] = None
        self._details_edit: Optional[QTextEdit] = None

        if details:
            self._details_button = QPushButton("Подробнее")
            self._details_button.setObjectName("DetailsButton")
            self._details_button.setCursor(Qt.PointingHandCursor)
            self._details_button.clicked.connect(self._toggle_details)

            layout.addWidget(self._details_button, alignment=Qt.AlignLeft)

            self._details_edit = QTextEdit()
            self._details_edit.setObjectName("DetailsEdit")
            self._details_edit.setReadOnly(True)
            self._details_edit.setPlainText(details)
            self._details_edit.hide()

            layout.addWidget(self._details_edit)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        self._timer: Optional[QTimer] = None
        if timeout and timeout > 0:
            self._timer = QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.close_toast)
            self._timer.start(timeout)

    def _toggle_details(self) -> None:
        if not self._details_edit:
            return
        self._details_visible = not self._details_visible
        if self._details_visible:
            self._details_edit.show()
            if self._details_button:
                self._details_button.setText("Скрыть детали")
        else:
            self._details_edit.hide()
            if self._details_button:
                self._details_button.setText("Подробнее")
        self.updateGeometry()
        parent = self.parent()
        if isinstance(parent, NotificationCenter):
            parent.reposition()

    def update_message(self, message: str, *, details: Optional[str] = None) -> None:
        self._message_label.setText(message)
        if details is not None and self._details_edit is not None:
            self._details_edit.setPlainText(details)

    def close_toast(self) -> None:
        if self._timer:
            self._timer.stop()
        self.closed.emit(self)
        self.deleteLater()


class ProgressToast(_ToastBase):
    def __init__(self, message: str, *, parent: Optional[QWidget] = None, details: Optional[str] = None) -> None:
        super().__init__(
            title="Выполнение операции",
            message=message,
            level="info",
            details=details,
            timeout=None,
            parent=parent,
        )

        from PySide2.QtWidgets import QProgressBar

        self._progress_bar = QProgressBar(self)
        self._progress_bar.setRange(0, 0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(4)
        self._progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: %s;
                border-radius: 2px;
            }
            """
            % self._accent
        )

        self.layout().addWidget(self._progress_bar)
        self._completion_timer: Optional[QTimer] = None

    def finish(self, *, success: bool = True, message: Optional[str] = None, details: Optional[str] = None) -> None:
        if message:
            self.update_message(message, details=details)

        self._progress_bar.setRange(0, 1)
        self._progress_bar.setValue(1 if success else 0)

        if not success:
            self._progress_bar.setStyleSheet(
                """
                QProgressBar {
                    background-color: rgba(239, 83, 80, 0.25);
                    border-radius: 2px;
                }
                QProgressBar::chunk {
                    background-color: #ef5350;
                    border-radius: 2px;
                }
                """
            )

        delay = 2000 if success else 5000
        self._completion_timer = QTimer(self)
        self._completion_timer.setSingleShot(True)
        self._completion_timer.timeout.connect(self.close_toast)
        self._completion_timer.start(delay)


class NotificationCenter(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        flags = Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        super().__init__(parent, flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)
        self._toasts: list[_ToastBase] = []

        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is self.parent() and event.type() in {QEvent.Resize, QEvent.Move}:
            QTimer.singleShot(0, self.reposition)
        return super().eventFilter(watched, event)

    def show_message(
        self,
        message: str,
        *,
        title: str = "Уведомление",
        level: str = "info",
        details: Optional[str] = None,
        timeout: Optional[int] = 6000,
    ) -> None:
        toast = _ToastBase(title=title, message=message, level=level, details=details, timeout=timeout, parent=self)
        self._register_toast(toast)

    def show_error(self, message: str, *, title: str = "Ошибка", details: Optional[str] = None) -> None:
        logger.error("%s: %s", title, message)
        toast = _ToastBase(title=title, message=message, level="error", details=details, timeout=None, parent=self)
        self._register_toast(toast)

    def show_success(self, message: str, *, title: str = "Готово", timeout: Optional[int] = 5000) -> None:
        toast = _ToastBase(title=title, message=message, level="success", timeout=timeout, parent=self)
        self._register_toast(toast)

    def show_progress(self, message: str, *, details: Optional[str] = None) -> ProgressToast:
        toast = ProgressToast(message=message, parent=self, details=details)
        self._register_toast(toast)
        return toast

    def _register_toast(self, toast: _ToastBase) -> None:
        toast.closed.connect(self._remove_toast)
        self._layout.addWidget(toast, 0, Qt.AlignRight)
        self._toasts.append(toast)
        toast.show()
        self.reposition()
        self.show()

    def _remove_toast(self, toast: _ToastBase) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            self._layout.removeWidget(toast)
        toast.hide()
        if not self._toasts:
            self.hide()
        QTimer.singleShot(0, self.reposition)

    def reposition(self) -> None:
        if not self.isVisible() and not self._toasts:
            return

        self.adjustSize()
        hint = self.sizeHint()

        parent = self.parentWidget()
        if parent:
            parent_rect = parent.frameGeometry()
            x = parent_rect.x() + parent_rect.width() - hint.width() - 24
            y = parent_rect.y() + parent_rect.height() - hint.height() - 24
        else:
            screen = QApplication.primaryScreen()
            geo: QRect
            if screen:
                geo = screen.availableGeometry()
            else:
                geo = QApplication.desktop().availableGeometry()
            x = geo.right() - hint.width() - 24
            y = geo.bottom() - hint.height() - 24

        self.move(QPoint(x, y))

