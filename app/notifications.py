from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QSizePolicy, QScrollArea, \
    QHBoxLayout, QFrame
from PySide2.QtCore import Qt, QTimer, QPoint


class Notification(QWidget):
    def __init__(self, text, timeout, parent=None, modern_theme=False):
        super().__init__(parent)

        # Set background color and rounded corners on frame
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)

        # Set label
        self.label = QLabel(self._get_short_text(text), self.frame)
        self.label.setToolTip(text)

        # Set close button
        self.close_button = QPushButton("×", self.frame)
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.remove_notification)

        self._modern_theme = modern_theme
        self.apply_theme(modern_theme)

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

    def apply_theme(self, modern_theme: bool):
        self._modern_theme = modern_theme
        if modern_theme:
            self.frame.setStyleSheet(
                "background-color: #ffffff; border-radius: 10px; border: 1px solid #dad3cb;"
            )
            self.label.setStyleSheet("color: #2f2b2a; padding: 10px;")
            self.close_button.setStyleSheet(
                """
    QPushButton {
        color: #ff7e67;
        font-weight: bold;
        background-color: transparent;
        border: none;
        margin-right: 8px;
    }
    QPushButton:hover {
        background-color: #ffe1d6;
        border-radius: 10px;
    }
    """
            )
        else:
            self.frame.setStyleSheet("background-color: #3c3f41; border-radius: 5px;")
            self.label.setStyleSheet("color: white; padding: 10px;")
            self.close_button.setStyleSheet(
                """
    QPushButton {
        color: white;
        font-weight: bold;
        background-color: transparent;
        border: none;
        margin-right: 5px;
    }
    QPushButton:hover {
        background-color: #2c2f30;
        border-radius: 10px;
    }
    """
            )


class StackedNotifications(QWidget):
    def __init__(self, parent=None, max_notifications=10, modern_theme=False):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.max_notifications = max_notifications
        self._modern_theme = modern_theme

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
        notification = Notification(text, timeout, self, self._modern_theme)
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

    def set_modern_theme(self, modern_theme: bool):
        self._modern_theme = modern_theme
        for notification in list(self._notifications):
            notification.apply_theme(modern_theme)
