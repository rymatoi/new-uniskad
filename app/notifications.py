from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QSizePolicy, QScrollArea, \
    QHBoxLayout, QFrame
from PySide2.QtCore import Qt, QTimer, QPoint


class Notification(QWidget):
    def __init__(self, text, timeout, parent=None):
        super().__init__(parent)

        self.frame = QFrame(self)
        self.frame.setObjectName("NotificationFrame")
        self.frame.setFrameShape(QFrame.StyledPanel)

        # Set label
        self.label = QLabel(self._get_short_text(text), self.frame)
        self.label.setObjectName("NotificationLabel")
        self.label.setStyleSheet("color: #f8fafc; padding: 10px;")
        self.label.setToolTip(text)

        # Set close button
        self.close_button = QPushButton("✕", self.frame)
        self.close_button.setObjectName("NotificationCloseButton")
        self.close_button.setFixedSize(28, 28)
        self.close_button.setCursor(Qt.PointingHandCursor)
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
        self.move(0, 0)

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

    def add_notification(self, text, timeout=5000):
        if len(self._notifications) >= self.max_notifications:
            self._notifications.pop(0)

        # Create notification and add to layout
        notification = Notification(text, timeout, self)
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

        # Update widget height
        self.update_height(notification)

        if self._notifications == 0:
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
        print(notification.height())
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
