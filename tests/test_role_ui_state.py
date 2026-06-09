import os
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')

from app import mainwindow as mainwindow_module
from app.mainwindow import MainWindow


def test_role_switch_captures_before_session_change_and_restores_after_menu_rebuild(monkeypatch):
    events = []
    old_role = SimpleNamespace(name='_role_100', rolename='User', id_role=100)
    new_role = SimpleNamespace(name='_role_200', rolename='Admin', id_role=200)
    controller = SimpleNamespace(
        roles=[old_role, new_role],
        current_role=old_role,
        available_actions=['old'],
        capture_ui_state=lambda: events.append('capture') or {'active_plugins': ['project']},
        _prepare_interface_for_role_switch=lambda: events.append('prepare_interface'),
        menuBar=lambda: SimpleNamespace(clear=lambda: events.append('clear_menu')),
        init_menu=lambda: events.append('init_menu'),
        connect_triggered_funcs=lambda: events.append('connect_actions'),
        restore_ui_state=lambda state, after_role_switch=False: events.append(
            ('restore', state, after_role_switch)
        ),
    )
    monkeypatch.setattr(
        mainwindow_module.sp,
        'set_sesion_role',
        lambda role_id: events.append(('set_sesion_role', role_id)) or True,
    )
    monkeypatch.setattr(
        mainwindow_module,
        'clear_menu_cache',
        lambda reason: events.append(('clear_menu_cache', reason)),
    )

    MainWindow.change_role(controller, new_role.name)

    assert events == [
        'capture',
        ('set_sesion_role', 200),
        ('clear_menu_cache', 'active role changed'),
        'prepare_interface',
        'clear_menu',
        'init_menu',
        'connect_actions',
        ('restore', {'active_plugins': ['project']}, True),
    ]
    assert controller.available_actions == []
    assert controller.current_role is new_role


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
