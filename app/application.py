from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QWidget

from app.interface_style import CONTAINER_STYLE_SHEET, FriendlyProxyStyle


class Application(QApplication):
    def __init__(self, *argv):
        super().__init__(*argv)
        self._default_font = QFont(self.font())
        self.setStyle(FriendlyProxyStyle(self.style()))
        self.setStyleSheet(CONTAINER_STYLE_SHEET)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_main_window)
        self.timer_disabled = False
        self._main_window_initialized = False
        self.time = 5
        self.disable_timer()

    def default_font(self):
        """Возвращает исходный системный шрифт приложения."""

        return QFont(self._default_font)

    def apply_interface_font(self, use_custom_font, font_name=None, font_size=None):
        """Задаёт базовый шрифт для всех элементов без собственного шрифта."""

        font = self.default_font()
        if use_custom_font:
            if font_name:
                font.setFamily(str(font_name))
            if font_size and int(font_size) > 0:
                font.setPointSize(int(font_size))
        self.setFont(font)
        self._update_existing_widget_fonts(font)

    def _update_existing_widget_fonts(self, interface_font):
        """Refresh already-created widgets while retaining emphasis and decoration.

        QApplication.setFont() becomes the default for newly created widgets, but
        widgets whose font was already resolved (for example custom dock headers
        and widgets with a stylesheet) can keep the previous point size.
        """

        for widget in self.allWidgets():
            if not isinstance(widget, QWidget) or widget.property("preserveInterfaceFont"):
                continue

            widget_font = QFont(widget.font())
            widget_font.setFamily(interface_font.family())
            if interface_font.pointSizeF() > 0:
                widget_font.setPointSizeF(interface_font.pointSizeF())
            elif interface_font.pixelSize() > 0:
                widget_font.setPixelSize(interface_font.pixelSize())
            widget.setFont(widget_font)
            widget.updateGeometry()
        self.processEvents()

    def initialize_main_window(self):
        self._main_window_initialized = True
        self.enable_timer()

    def deinitialize_main_window(self):
        self._main_window_initialized = False
        self.disable_timer()

    def close_main_window(self):
        if not self.timer_disabled and self._main_window_initialized:
            self.disable_timer()
            for window in self.allWidgets():
                if isinstance(window, (QMainWindow, QDialog)):
                    window.close()

    def disable_timer(self):
        self.timer_disabled = True
        self.timer.stop()

    def enable_timer(self, timer_time=None):
        self.time = timer_time
        self.timer_disabled = False
        if timer_time:
            self.timer.start(int(self.time) * 60 * 1000)
        else:
            self.timer.start(30 * 60 * 1000)

        #self.timer.start()

    def notify(self, receiver, event):
        if isinstance(event, QKeyEvent) or isinstance(event, QMouseEvent):
            self.timer.start(int(self.time) * 60 * 1000)
        return super().notify(receiver, event)
