from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')

from PySide2.QtWidgets import QApplication, QDialog

from app.mainwindow import MainWindow
from app.plugins.admin_users.models import AdminUsersTreeModel, USER_COLUMNS, UserNode
from db._session import Session
from dialogs.login import LoginDialog


def _application():
    return QApplication.instance() or QApplication([])


class _CloseEvent:
    def __init__(self):
        self.accepted = False
        self.ignored = False

    def accept(self):
        self.accepted = True

    def ignore(self):
        self.ignored = True


def test_close_event_cancel_keeps_window_open():
    window = SimpleNamespace(_close_without_prompt=False, _ask_close_action=lambda: 'cancel')
    event = _CloseEvent()

    MainWindow.closeEvent(window, event)

    assert event.ignored is True
    assert event.accepted is False


def test_session_logout_clears_credentials_and_menu_cache():
    session = Session.__new__(Session)
    session._login = 'old-user'
    session._password = 'secret'
    session.main_window = object()
    reasons = []
    session._clear_menu_cache = reasons.append

    session.logout()

    assert session._login is None
    assert session._password is None
    assert session.main_window is None
    assert reasons == ['user logged out']


def _login_dialog(monkeypatch, user):
    _application()
    monkeypatch.setattr('dialogs.login.sp.checkuserpassword', lambda *_args: True)
    monkeypatch.setattr('dialogs.login.sp.get_full_users_list', lambda: [user])
    dialog = LoginDialog()
    dialog.ui.username.setText(user.login)
    dialog.ui.password.setText('password')
    return dialog


def test_blocked_user_cannot_login(monkeypatch):
    user = SimpleNamespace(login='blocked', active=False, deleted=False)
    logout_calls = []
    monkeypatch.setattr('dialogs.login.session.logout', lambda: logout_calls.append(True))
    dialog = _login_dialog(monkeypatch, user)

    dialog.login()

    assert dialog.result() != QDialog.Accepted
    assert dialog.ui.errorBox.text() == 'Пользователь заблокирован. Обратитесь к администратору.'
    assert logout_calls == [True]


def test_active_user_login_is_unchanged(monkeypatch):
    user = SimpleNamespace(login='active', active=True, deleted=False)
    dialog = _login_dialog(monkeypatch, user)

    dialog.login()

    assert dialog.result() == QDialog.Accepted


def test_admin_user_tree_displays_only_full_name_and_login():
    user = SimpleNamespace(login='ivanov', fam='Иванов', name='Иван')
    node = UserNode(user)
    model = AdminUsersTreeModel()

    values = [node.data(column) for column in range(node.columnCount())]

    assert USER_COLUMNS == ('ФИО', 'Логин')
    assert model.headers == ['ФИО', 'Логин']
    assert node.columnCount() == 2
    assert values == ['Иванов Иван', 'ivanov']
