from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFrame
from PySide2.QtCore import Qt, QTimer


class Notification(QWidget):
    def __init__(self, text, timeout, parent=None, use_modern_theme=False):
        super().__init__(parent)

        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)

        self.label = QLabel(self._get_short_text(text), self.frame)
        self.label.setToolTip(text)

        self.close_button = QPushButton("✕", self.frame)
        self.close_button.setFixedSize(24, 24)
        self.close_button.clicked.connect(self.remove_notification)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.remove_notification)
        self.timer.start(timeout)

        layout = QHBoxLayout(self.frame)
        layout.addWidget(self.label)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)

        container_layout = QHBoxLayout(self)
        container_layout.addWidget(self.frame)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.apply_theme(use_modern_theme)
        self.adjustSize()
        self.move(0, 0)

    def apply_theme(self, use_modern_theme):
        if use_modern_theme:
            self.frame.setStyleSheet(
                """
                QFrame {
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #dfe3eb;
                }
                """
            )
            self.label.setStyleSheet("color: #1c1f26; padding: 2px 0; font-weight: 500;")
            self.close_button.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #8a96ad;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(52, 120, 246, 0.1);
                    color: #1c1f26;
                    border-radius: 12px;
                }
                """
            )
        else:
            self.frame.setStyleSheet("background-color: #3c3f41; border-radius: 5px;")
            self.label.setStyleSheet("color: white; padding: 2px 0;")
            self.close_button.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    font-weight: bold;
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2c2f30;
                    border-radius: 12px;
                }
                """
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
        if self.parent():
            self.parent().remove_notification(self)


class StackedNotifications(QWidget):
    def __init__(self, parent=None, max_notifications=10):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.max_notifications = max_notifications
        self.use_modern_theme = False

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

    def add_notification(self, text, timeout=5000):
        if len(self._notifications) >= self.max_notifications:
            oldest = self._notifications.pop(0)
            self.layout.removeWidget(oldest)
            oldest.deleteLater()

        # Create notification and add to layout
        notification = Notification(text, timeout, self, self.use_modern_theme)
        self._notifications.append(notification)
        self.layout.addWidget(notification)

        # Show notification
        notification.show()

        # Update widget height
        self.update_height(notification)

        # Set timer to update position after showing the notification
        QTimer.singleShot(100, self.update_position)

        # Set timer to remove notification after timeout
        QTimer.singleShot(timeout, lambda: self.remove_notification(notification))

    def remove_notification(self, notification):
        # Remove notification from layout
        self.layout.removeWidget(notification)
        if notification in self._notifications:
            self._notifications.remove(notification)

        # Update widget height
        self.update_height(notification)

        notification.deleteLater()

        if not self._notifications:
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

    def update_height(self, notification):
        # Get number of notifications in layout
        count = self.layout.count()

        # Calculate new height
        if count == 0:
            new_height = 0
        else:
            new_height = count * (self.notification_height + self.spacing) + self.spacing

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

    def set_modern_theme(self, enabled: bool):
        self.use_modern_theme = enabled
        for notification in list(self._notifications):
            notification.apply_theme(enabled)
