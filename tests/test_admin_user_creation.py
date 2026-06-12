import os
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')
pytest.importorskip('asyncpg')

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QWidget

from app.plugins.admin_users.dialogs.create_user import CreateUserDialog
from app.plugins.admin_users.models import UserNode
from app.plugins.base_state.models import TreeModel
from app.plugins.base_state.widgets import TreeView


@pytest.fixture
def application():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    ('field_name', 'expected_message'),
    (
        ('secondname_line_edit', 'Заполните фамилию пользователя'),
        ('username_line_edit', 'Заполните логин пользователя'),
        ('password_line_edit', 'Заполните пароль пользователя'),
    ),
)
def test_create_user_dialog_rejects_empty_required_fields(
    application, monkeypatch, field_name, expected_message
):
    role = SimpleNamespace(rolename='Администратор', prop_name='name', deleted=False, id=1)
    monkeypatch.setattr('app.plugins.admin_users.dialogs.create_user.sp.get_roles', lambda: [role])
    messages = []
    monkeypatch.setattr(
        'app.plugins.admin_users.dialogs.create_user.error',
        lambda title, text: messages.append((title, text)),
    )

    dialog = CreateUserDialog()
    dialog.username_line_edit.setText('new-user')
    dialog.password_line_edit.setText('password')
    dialog.firstname_line_edit.setText('Имя')
    dialog.secondname_line_edit.setText('Фамилия')
    getattr(dialog, field_name).setText('   ')

    dialog.create_user()

    assert dialog.get_result() is None
    assert dialog.result() == 0
    assert messages == [('Ошибка создания пользователя', expected_message)]


def test_user_creation_database_error_is_not_returned_as_tree_node(monkeypatch):
    database_error = RuntimeError('sc_ref.new_uniskaduser- user_fam cannot be empty!')

    class AcceptedDialog:
        def exec_(self):
            return True

        def get_result(self):
            return (50, 'login', 'password', 'Фамилия', 'Имя', 1)

    messages = []
    monkeypatch.setattr('app.plugins.admin_users.models.CreateUserDialog', AcceptedDialog)
    monkeypatch.setattr('app.plugins.admin_users.models.sp.new_uniskaduser', lambda *_args: database_error)
    monkeypatch.setattr(
        'app.plugins.admin_users.models.error',
        lambda title, text: messages.append((title, text)),
    )

    assert UserNode.add(0, None) is None
    assert messages == [('Ошибка создания пользователя', str(database_error))]


def test_tree_view_does_not_insert_database_error(application, monkeypatch):
    monkeypatch.setattr(TreeView, '_load_menu', lambda *_args, **_kwargs: [])
    messages = []
    monkeypatch.setattr(
        'app.plugins.base_state.widgets.basic_funcs.error',
        lambda title, text: messages.append((title, text)),
    )

    view = TreeView(QWidget())
    model = TreeModel()
    view.setModel(model)
    add_child_calls = []
    monkeypatch.setattr(model, 'addChild', lambda *args: add_child_calls.append(args))
    database_error = RuntimeError('database rejected item')

    result = view._add_item(database_error, QModelIndex(), model.root_id, model._root)

    assert result is False
    assert add_child_calls == []
    assert model.rowCount() == 0
    assert messages == [('Ошибка добавления элемента', str(database_error))]


def test_tree_view_handles_raised_creation_error_without_inserting(application, monkeypatch):
    monkeypatch.setattr(TreeView, '_load_menu', lambda *_args, **_kwargs: [])
    messages = []
    monkeypatch.setattr(
        'app.plugins.base_state.widgets.basic_funcs.error',
        lambda title, text: messages.append((title, text)),
    )

    class FailingNodeType:
        @staticmethod
        def add(_up_node_id, _parent):
            raise RuntimeError('database call failed')

    view = TreeView(QWidget())
    model = TreeModel()
    model.item_types['failing'] = FailingNodeType
    view.setModel(model)
    add_child_calls = []
    monkeypatch.setattr(model, 'addChild', lambda *args: add_child_calls.append(args))

    result = view.add_item('failing', QModelIndex())

    assert result is False
    assert add_child_calls == []
    assert model.rowCount() == 0
    assert messages == [('Ошибка добавления элемента', 'database call failed')]


def test_tree_model_add_child_rejects_unsupported_object_without_attribute_error():
    model = TreeModel()

    assert model.addChild(RuntimeError('database rejected item'), QModelIndex()) is False
    assert model.rowCount() == 0
