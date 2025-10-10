from typing import Optional

from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QSizePolicy, QScrollArea, \
    QHBoxLayout, QFrame
from PySide2.QtCore import Qt, QTimer, QPoint
from PySide2.QtGui import QPalette, QColor


class Notification(QWidget):
    def __init__(self, text, timeout, parent=None):
        super().__init__(parent)

        # Set background color and rounded corners on frame
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)

        # Set label
        self.label = QLabel(self._get_short_text(text), self.frame)
        self.label.setToolTip(text)

        # Set close button
        self.close_button = QPushButton("X", self.frame)
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.remove_notification)

        # Set timer to hide notification after timeout
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.remove_notification)
        self.timer.start(timeout)

        # Set layout
        layout = QHBoxLayout(self.frame)
        layout.addWidget(self.label)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(0, 0, 0, 0)

        # Set layout and position
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.frame)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.adjustSize()
        self.apply_palette(QApplication.instance().palette())
        self.move(0, 0)

    def apply_palette(self, palette: Optional[QPalette]) -> None:
        if palette is None:
            return

        base = QColor(palette.color(QPalette.Base))
        text = QColor(palette.color(QPalette.Text))
        accent = QColor(palette.color(QPalette.Highlight))
        border_color = QColor(accent)
        border_color = border_color.lighter(150)

        hover_color = QColor(accent)
        hover_color = hover_color.lighter(140)
        hover_rgba = f"rgba({hover_color.red()}, {hover_color.green()}, {hover_color.blue()}, 60)"

        self.frame.setStyleSheet(
            f"background-color: {base.name()};"
            f"border-radius: 14px;"
            f"border: 1px solid {border_color.name()};"
            f"padding: 0;"
        )
        self.label.setStyleSheet(
            f"color: {text.name()};"
            f"padding: 10px 14px;"
        )
        self.close_button.setStyleSheet(
            """
            QPushButton {{
                color: {text_color};
                background-color: transparent;
                border: none;
                font-weight: bold;
                margin-right: 6px;
            }}
            QPushButton:hover {{
                border-radius: 10px;
                background-color: {hover_rgba};
            }}
            """.format(hover_rgba=hover_rgba, text_color=text.name())
        )

    def _get_short_text(self, text):
        """
        Сокращение текста уведомления. Нужно, потому что не могу пока сделать динамическое изменение высоты уведомления
        """
        if len(text) > 50:
            return text[:47] + "..."
        else:
            return text

    def remove_notification(self):
        self.parent().remove_notification(self)
        # self.deleteLater()


class StackedNotifications(QWidget):
    def __init__(self, parent=None, max_notifications=10):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.max_notifications = max_notifications

        # Set background color to transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.spacing = 10
        self.layout.setSpacing(self.spacing)

        # Set maximum width
        self.setMaximumWidth(400)

        # Set notification height
        self.notification_height = 33

        # Set initial height
        self.height = 0

        self._notifications = []

        # Set position of the notification widget
        self.update_position()
        self.apply_palette()

    def add_notification(self, text, timeout=5000):
        if len(self._notifications) >= self.max_notifications:
            old = self._notifications.pop(0)
            self.layout.removeWidget(old)
            old.deleteLater()

        # Create notification and add to layout
        notification = Notification(text, timeout, self)
        self._notifications.append(notification)
        self.layout.addWidget(notification)

        # Show notification
        notification.show()

        # Update widget height
        self.update_height()

        # Set timer to update position after showing the notification
        QTimer.singleShot(100, self.update_position)

        # Set timer to remove notification after timeout
        QTimer.singleShot(timeout, lambda: self.remove_notification(notification))
        notification.apply_palette(QApplication.instance().palette())

    def remove_notification(self, notification):
        # Remove notification from layout
        self.layout.removeWidget(notification)
        if notification in self._notifications:
            self._notifications.remove(notification)
        notification.deleteLater()

        # Update widget height
        self.update_height()

        if len(self._notifications) == 0:
            self.hide()

    def update_position(self):
        # Get screen geometry and widget size
        screen = QApplication.desktop().screenGeometry(self)
        widget_rect = self.geometry()

        # Calculate position of the notification widget
        x = screen.right() - widget_rect.width() - 20
        y = screen.bottom() - widget_rect.height() - 20

        # Set position of the notification widget
        self.move(x, y)

    def update_height(self):
        # Get number of notifications in layout
        count = self.layout.count()

        # Calculate new height
        new_height = max(0, count * (self.notification_height + self.spacing) + self.spacing)

        # If the new height is greater than the current height, increase the widget height
        if new_height > self.height:
            self.height = new_height
            self.setFixedHeight(self.height)

        # If the new height is less than the current height, decrease the widget height
        elif new_height < self.height:
            self.height = new_height
            self.setFixedHeight(self.height)

        # Set position of the notification widget
        self.update_position()

    def apply_palette(self):
        palette = QApplication.instance().palette()
        if palette is None:
            return
        for notification in self._notifications:
            notification.apply_palette(palette)
