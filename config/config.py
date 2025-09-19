import base64
import os.path

from PySide2 import QtWidgets
from PySide2.QtCore import QSettings, QTranslator, QLocale, QLibraryInfo
from PySide2.QtWidgets import QDialog
from cryptography.fernet import Fernet

from app import app_logger
from app.application import Application
from dialogs.create_config import CreateConfigDialog

app = Application()  # создание экземпляра приложения
translator = QTranslator()

# translator.load('qt_' + QLocale.system().name(), QLibraryInfo.location(QLibraryInfo.TranslationsPath))
val = translator.load('qt_' + QLocale.system().name(), os.path.normpath('./resources/translation/'))
# val = translator.load("qt_ru.qm", './resources/translation/')
app.installTranslator(translator)

app.setStyle('Fusion')  # определяем стиль приложения
CONFIG_FILE = "config/config2.ini"  # путь к конфиг-файлу
APP_FERNET_KEY = b"057839653fd345xx9530ssrxc4562d55"  # ключ шифрованию

DB_MENU = False
PROG_ID = 50

logger = app_logger.get_logger(__name__)  # подключаем экземпляр логгера для логирования


class Config:
    def __init__(self):
        self.settings = Settings()
        if not os.path.exists(CONFIG_FILE):
            logger.info('Конфигурационный файл не найден. Создание нового конфигурационного файла.')
            self.create()

    def create(self):
        create_config_dialog = CreateConfigDialog()
        if create_config_dialog.exec_() == QDialog.Accepted:
            config_data = create_config_dialog.get_result()
            self.settings.save('host', config_data.rhost, 'remote_database')
            self.settings.save('port', config_data.rport, 'remote_database')
            self.settings.save('username', config_data.rusername, 'remote_database')
            self.settings.save('password', config_data.rpassword, 'remote_database')
            self.settings.save('database', config_data.rdatabase, 'remote_database')

            # self.settings.save('host', config_data.lhost, 'local_database')
            # self.settings.save('port', config_data.lport, 'local_database')
            # self.settings.save('username', config_data.lusername, 'local_database')
            # self.settings.save('password', config_data.lpassword, 'local_database')
            # self.settings.save('database', config_data.ldatabase, 'local_database')

            self.settings.save('level', config_data.level, 'logging')
            self.settings.save('filename', config_data.filename, 'logging')

            logger.info('Конфигурационный файл успешно создан. Вход в программу.')
        else:
            logger.error('Конфигурационный файл не задан. Выход из программы.')
            app.exit()

    def get_remote_db_url(self):
        """ Создание строки подключения к базе данных """
        # url = f"host='{self.settings.load('host', '', 'remote_database')}' " \
        #       f"dbname='{self.settings.load('database', '', 'remote_database')}'" \
        #       f"user='{self.settings.load('username', '', 'remote_database')}'" \
        #       f"password='{self.settings.load('password', '', 'remote_database')}'" \
        #       f"port={self.settings.load('port', '', 'remote_database')}"
        # return url

        return f"postgres://{self.settings.load('username', '', 'remote_database')}:{self.settings.load('password', '', 'remote_database')}@{self.settings.load('host', '', 'remote_database')}:{self.settings.load('port', '', 'remote_database')}/{self.settings.load('database', '', 'remote_database')}?"

    def get_local_db_url(self):
        """ Создание строки подключения к базе данных """
        url = f"host='{self.settings.load('host', '', 'local_database')}' " \
              f"dbname='{self.settings.load('database', '', 'local_database')}'" \
              f"user='{self.settings.load('username', '', 'local_database')}'" \
              f"password='{self.settings.load('password', '', 'local_database')}'" \
              f"port={self.settings.load('port', '', 'local_database')}"
        return url

    def get_old_db_url(self):
        """ Создание строки подключения к базе данных """
        pass

    def get_fernet_key(self) -> Fernet:
        return Fernet(base64.urlsafe_b64encode(APP_FERNET_KEY))


class Settings:
    """ Работа с ключами конфиг-файла """

    # Инициализация экземпляра класса "Settings"
    def __init__(self, config_path=CONFIG_FILE):
        self.settings = QSettings(config_path, QSettings.IniFormat)

    # Создание и возврат экземпляра библиотечного класса FERNET, который содержит методы шифрования/дешифрования
    def get_fernet_key(self) -> Fernet:
        return Fernet(base64.urlsafe_b64encode(APP_FERNET_KEY))

    # Сохранить ключ
    def save(self, key, value, group):
        self.settings.beginGroup(group)  # Находим группу параметров "group" в INI-файле и делаем её "текущей"
        f = self.get_fernet_key()  # Получаем экземпляр библиотечного класса FERNET
        token = f.encrypt(str.encode(str(value), encoding='utf-8'))  # Шифруем
        # Сохраняем зашифрованный параметр как строку
        self.settings.setValue(key, bytes.decode(token, encoding='utf-8'))
        self.settings.endGroup()  # Группа параметров "group" теперь не является "текущей"

    # Загрузить ключ
    def load(self, key, default, group):
        self.settings.beginGroup(group)  # Находим группу параметров "group" в INI-файле и делаем её "текущей"
        f = self.get_fernet_key()  # Получаем экземпляр библиотечного класса FERNET
        # Получаем зашифрованное значение ключа из конфиг-файла
        token = str(self.settings.value(key, default, type=str))
        if token == default:
            self.settings.endGroup()  # Группа параметров "group" теперь не является "текущей"
            return default  # Ключа нет - возврат значения по умолчанию
        # расшифровываем  начение ключа из конфиг-файла
        value = bytes.decode(f.decrypt(str.encode(token, encoding='utf-8')), encoding='utf-8')
        self.settings.endGroup()  # Группа параметров "group" теперь не является "текущей"
        return value  # Возврат расшифрованного значения ключа

    # Проверить наличие ключа
    def check_key(self, key, group):
        self.settings.beginGroup(group)  # Находим группу параметров "group" в INI-файле и делаем её "текущей"
        retval = self.settings.contains(key)  # Получаем флаг True - ключ существует ,False - нет
        self.settings.endGroup()  # Группа параметров "group" теперь не является "текущей"
        return retval


config = Config()
