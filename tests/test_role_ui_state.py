import os
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')

from PySide2.QtCore import QByteArray

from app import mainwindow as mainwindow_module
from app.mainwindow import MainWindow


class FakeSettings:
    def __init__(self):
        self.values = {
            'remember_last_session': True,
            'restore_window_layout': True,
            'restore_last_project': True,
        }

    def get(self, key, default=None):
        return self.values.get(key, default)

    def get_bytes(self, key):
        value = self.values.get(key)
        return QByteArray(value) if isinstance(value, QByteArray) else QByteArray()

    def set(self, key, value):
        self.values[key] = value

    def remove(self, key):
        self.values.pop(key, None)

    def contains(self, key):
        return key in self.values


def make_state_controller(settings, current_role, captured_states=None):
    restored = []
    captured_states = captured_states or {}
    controller = SimpleNamespace(
        user=SimpleNamespace(login='alice/example'),
        current_role=current_role,
        user_settings=settings,
        _tree_states_to_restore={},
        dock_widgets={},
        _coerce_bool=MainWindow._coerce_bool,
        _coerce_tree_states=MainWindow._coerce_tree_states,
        _ui_state_key=lambda role=None: MainWindow._ui_state_key(controller, role),
        _ui_state_setting=lambda name, role=None: MainWindow._ui_state_setting(controller, name, role),
        capture_ui_state=lambda **kwargs: captured_states[kwargs.get('role').id_role],
        restore_ui_state=lambda state, after_role_switch=False: restored.append((state, after_role_switch)) or True,
    )
    return controller, restored


def test_ui_state_is_saved_and_restored_per_login_and_role():
    role_a = SimpleNamespace(id_role=100)
    role_b = SimpleNamespace(id_role=200)
    settings = FakeSettings()
    states = {
        100: {'active_plugins': ['project'], 'tree_states': {'project': {'open_tabs': ['A']}}},
        200: {'active_plugins': ['work_data'], 'tree_states': {'work_data': {'open_tabs': ['B']}}},
    }
    controller, restored = make_state_controller(settings, role_a, states)

    MainWindow.save_ui_state(controller, role=role_a)
    MainWindow.save_ui_state(controller, role=role_b)
    MainWindow.restore_saved_ui_state(controller, role=role_b, after_role_switch=True)
    MainWindow.restore_saved_ui_state(controller, role=role_a, after_role_switch=True)

    key_a = 'ui_state/alice%2Fexample/100'
    key_b = 'ui_state/alice%2Fexample/200'
    assert settings.values[f'{key_a}/active_plugins'] == ['project']
    assert settings.values[f'{key_b}/active_plugins'] == ['work_data']
    assert restored[0][0]['active_plugins'] == ['work_data']
    assert restored[1][0]['active_plugins'] == ['project']


def test_role_switch_saves_old_role_and_restores_new_role_after_menu_rebuild(monkeypatch):
    events = []
    old_role = SimpleNamespace(name='_role_100', rolename='User', id_role=100)
    new_role = SimpleNamespace(name='_role_200', rolename='Admin', id_role=200)
    controller = SimpleNamespace(
        roles=[old_role, new_role],
        current_role=old_role,
        available_actions=['old'],
        save_ui_state=lambda **kwargs: events.append(('save', kwargs['role'].id_role)),
        _prepare_interface_for_role_switch=lambda: events.append('prepare_interface'),
        menuBar=lambda: SimpleNamespace(clear=lambda: events.append('clear_menu')),
        init_menu=lambda: events.append('init_menu'),
        connect_triggered_funcs=lambda: events.append('connect_actions'),
        restore_saved_ui_state=lambda **kwargs: events.append(('restore', kwargs['role'].id_role)),
    )
    monkeypatch.setattr(mainwindow_module.sp, 'set_sesion_role',
                        lambda role_id: events.append(('set_sesion_role', role_id)) or True)
    monkeypatch.setattr(mainwindow_module, 'clear_menu_cache',
                        lambda reason: events.append(('clear_menu_cache', reason)))

    MainWindow.change_role(controller, new_role.name)

    assert events == [
        ('save', 100),
        ('set_sesion_role', 200),
        ('clear_menu_cache', 'active role changed'),
        'prepare_interface',
        'clear_menu',
        'init_menu',
        'connect_actions',
        ('restore', 200),
    ]
    assert controller.current_role is new_role

    events.clear()
    MainWindow.change_role(controller, old_role.name)

    assert events == [
        ('save', 200),
        ('set_sesion_role', 100),
        ('clear_menu_cache', 'active role changed'),
        'prepare_interface',
        'clear_menu',
        'init_menu',
        'connect_actions',
        ('restore', 100),
    ]
    assert controller.current_role is old_role


def test_missing_role_state_restores_defaults_not_previous_role_state():
    role_a = SimpleNamespace(id_role=100)
    role_b = SimpleNamespace(id_role=200)
    settings = FakeSettings()
    states = {100: {'active_plugins': ['project']}}
    controller, restored = make_state_controller(settings, role_a, states)

    MainWindow.save_ui_state(controller, role=role_a)
    MainWindow.restore_saved_ui_state(controller, role=role_b, after_role_switch=True)

    assert restored == [({
        'tree_states': {},
        'active_project': None,
        'active_plugins': [],
    }, True)]


def test_restore_ui_state_skips_forbidden_and_missing_modes_without_crashing():
    activated = []
    controller = SimpleNamespace(
        ADMIN_ROLES=MainWindow.ADMIN_ROLES,
        ADMIN_USERS=MainWindow.ADMIN_USERS,
        WORK_DATA=MainWindow.WORK_DATA,
        SYNONYM_DICTIONARY=MainWindow.SYNONYM_DICTIONARY,
        EIZM_DICTIONARY=MainWindow.EIZM_DICTIONARY,
        PROJECT=MainWindow.PROJECT,
        available_actions=[],
        project=None,
        _restoring_after_role_switch=False,
        _pending_window_state_bytes=None,
        _pending_central_window_state_bytes=None,
        _tree_states_to_restore={},
        _coerce_tree_states=MainWindow._coerce_tree_states,
        _plugin_restore_action=lambda plugin: MainWindow._plugin_restore_action(controller, plugin),
        activate_tree=lambda *args: activated.append(args),
        _apply_pending_window_state=lambda: None,
        _enforce_role_restore_visibility=lambda: None,
    )

    result = MainWindow.restore_ui_state(
        controller,
        {
            'active_plugins': ['project', 'unknown_mode'],
            'tree_states': {'project': {'open_tabs': ['101']}},
        },
        after_role_switch=True,
    )

    assert result is True
    assert activated == []
    assert controller._tree_states_to_restore == {}
    assert controller._restoring_after_role_switch is False
