import locale
import sys

from PySide2.QtWidgets import QDialog

from app import app_logger
from config import config
import db
import resources.resources_rc
from dialogs.login import LoginDialog
from app.mainwindow import MainWindow

logger = app_logger.get_logger(__name__)

from PySide2.QtCore import QLocale


def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    if issubclass(exc_type, RecursionError):
        message = 'Обнаружено переполнение стека.'
    else:
        message = 'Необработанное исключение.'

    logger.critical(message, exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = log_unhandled_exception


# Устанавливаем локаль для конкретных элементов приложения
def set_locale():
    """ Due to different locale (decimal point is ,) in some countries
        So for decimal point being . for all users it must be Specified here the beginning
    """
    want_locale = QLocale(QLocale.English, QLocale.Europe)
    QLocale.setDefault(want_locale)


def create_login_dialog():
    dialog = LoginDialog()
    return dialog


if __name__ == '__main__':
    #set_locale()
    login = create_login_dialog()
    if login.exec_() == QDialog.Accepted:
        window = MainWindow()
        logger.info('Программа запущена.')
        window.showMaximized()
        sys.exit(config.app.exec_())
