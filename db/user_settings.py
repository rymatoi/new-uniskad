import asyncio

from db import sp


class UserSettings:

    def __init__(self):
        self.load_settings()

    def update(self):
        self.load_settings()

    def load_settings(self):
        settings = sp.get_user_default_values(None, None)
        for setting in settings:
            setattr(self, setting.u_prm_name, setting.prm_value)

    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return default
