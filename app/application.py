from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog


class Application(QApplication):
    def __init__(self, *argv):
        super().__init__(*argv)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_main_window)
        self.timer_disabled = False
        self._main_window_initialized = False
        self.time = 5
        self.disable_timer()

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
