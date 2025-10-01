from PySide2.QtCore import QSettings


class UserSettings:

    ORGANIZATION = "Uniskad"
    APPLICATION = "NewUniskad"

    def __init__(self):
        self._settings = QSettings(self.ORGANIZATION, self.APPLICATION)
        self.load_settings()

    def update(self):
        self.load_settings()

    def load_settings(self):
        for key in self._settings.allKeys():
            setattr(self, key, self._settings.value(key))

    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)

        value = self._settings.value(name, default)
        if value is None:
            return default

        setattr(self, name, value)
        return value

    def set(self, name, value):
        self._settings.setValue(name, value)
        setattr(self, name, value)
        self._settings.sync()
