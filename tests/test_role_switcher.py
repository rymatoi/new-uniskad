import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide2")

from PySide2.QtWidgets import QApplication, QGroupBox, QWidget

from settings.dialog import SettingsDialog
from widgets.role_switcher import RoleSwitcherWidget


class DummySettings:
    def get(self, name, default=None):
        return default


class RoleController(QWidget):
    def __init__(self):
        super().__init__()
        self.user_settings = DummySettings()
        self.roles = [
            SimpleNamespace(name="_role_100", rolename="Пользователь"),
            SimpleNamespace(name="_role_200", rolename="Администратор"),
        ]
        self.current_role = self.roles[0]
        self.changed_roles = []

    def change_role(self, role_name):
        self.changed_roles.append(role_name)
        self.current_role = next(role for role in self.roles if role.name == role_name)

    def create_role_switcher(self, parent=None):
        return RoleSwitcherWidget(self, parent)


def application():
    return QApplication.instance() or QApplication([])


def test_role_switcher_delegates_change_and_displays_current_role():
    application()
    controller = RoleController()
    switcher = RoleSwitcherWidget(controller)

    assert switcher.button.text() == "Пользователь"

    switcher.button.menu().actions()[1].trigger()

    assert controller.changed_roles == ["_role_200"]
    assert switcher.button.text() == "Администратор"


def test_settings_general_tab_places_role_switcher_group_first():
    application()
    controller = RoleController()
    dialog = SettingsDialog(controller)

    first_group = dialog.general_tab.layout().itemAt(0).widget()

    assert isinstance(first_group, QGroupBox)
    assert first_group.title() == "Роль пользователя"
    assert first_group.findChild(RoleSwitcherWidget) is not None
