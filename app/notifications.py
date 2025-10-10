from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFrame
from PySide2.QtCore import Qt, QTimer


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
        self.close_button.setFixedSize(24, 24)
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

        self.refresh_theme()

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

    def refresh_theme(self):
        modern_ui = bool(QApplication.instance().property("modern_ui_enabled"))
        if modern_ui:
            frame_style = (
                "QFrame {"
                "background-color: #ffffff;"
                "border-radius: 16px;"
                "border: 1px solid #d9e2f6;"
                "padding: 4px 12px;"
                "}"
            )
            label_style = (
                "QLabel {"
                "color: #1f2d5c;"
                "padding: 12px 8px;"
                "font-weight: 500;"
                "}"
            )
            close_style = (
                "QPushButton {"
                "color: #6f7d95;"
                "font-weight: bold;"
                "background-color: transparent;"
                "border: none;"
                "border-radius: 12px;"
                "}"
                "QPushButton:hover {"
                "color: #1f2d5c;"
                "background-color: rgba(111, 139, 255, 0.18);"
                "}"
            )
        else:
            frame_style = "QFrame {background-color: #3c3f41; border-radius: 5px;}"
            label_style = "QLabel {color: white; padding: 10px;}"
            close_style = (
                "QPushButton {"
                "color: white;"
                "font-weight: bold;"
                "background-color: transparent;"
                "border: none;"
                "margin-right: 5px;"
                "}"
                "QPushButton:hover {"
                "background-color: #2c2f30;"
                "border-radius: 10px;"
                "}"
            )

        self.frame.setStyleSheet(frame_style)
        self.label.setStyleSheet(label_style)
        self.close_button.setStyleSheet(close_style)


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
        self.spacing = 12
        self.layout.setSpacing(self.spacing)

        # Set maximum width
        self.setMaximumWidth(420)

        # Set notification height
        self.notification_height = 48

        # Set initial height
        self.height = 0

        self._notifications = []

        # Set position of the notification widget
        self.update_position()
        self.refresh_theme()

    def add_notification(self, text, timeout=5000):
        if len(self._notifications) >= self.max_notifications:
            old_notification = self._notifications.pop(0)
            self.layout.removeWidget(old_notification)
            old_notification.deleteLater()

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

    def remove_notification(self, notification):
        # Remove notification from layout
        self.layout.removeWidget(notification)
        if notification in self._notifications:
            self._notifications.remove(notification)

        # Update widget height
        self.update_height()

        notification.deleteLater()

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

        if new_height != self.height:
            self.height = new_height
            self.setFixedHeight(self.height)

        # Set position of the notification widget
        self.update_position()

    def refresh_theme(self):
        modern_ui = bool(QApplication.instance().property("modern_ui_enabled"))
        self.spacing = 16 if modern_ui else 12
        self.layout.setSpacing(self.spacing)
        self.notification_height = 56 if modern_ui else 33
        for index in range(self.layout.count()):
            item = self.layout.itemAt(index)
            widget = item.widget()
            if isinstance(widget, Notification):
                widget.refresh_theme()
        self.update_height()
