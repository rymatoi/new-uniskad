import os
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')

from app.plugins.base_state.models import Node


def test_node_rows_are_reindexed_after_insert_remove_and_sort():
    parent = Node(None)
    first, second, third = Node(None), Node(None), Node(None)

    parent.addChild(first)
    parent.addChild(third)
    parent.insertChildren(1, [second])

    assert [child.row() for child in parent.children] == [0, 1, 2]

    parent.removeChild(0)
    assert [child.row() for child in parent.children] == [0, 1]
    assert first.parent() is None
    assert first.row() == 0

    parent.children.reverse()
    parent._reindex_children()
    assert [child.row() for child in parent.children] == [0, 1]


def _tree_data(node_id, deleted=False):
    return SimpleNamespace(
        id=node_id,
        id_up=0,
        type_='root',
        prop_name='name',
        prop_value='Node {}'.format(node_id),
        deleted=deleted,
    )


def test_tree_model_tracks_whether_deleted_nodes_exist():
    from app.plugins.base_state.models import TreeModel

    active_model = TreeModel()
    active_model.ini_tree([_tree_data(1)])

    deleted_model = TreeModel()
    deleted_model.ini_tree([_tree_data(2, deleted=True)])

    assert active_model.has_deleted_nodes is False
    assert deleted_model.has_deleted_nodes is True


def test_tree_view_only_schedules_refresh_for_model_with_deleted_nodes(monkeypatch):
    from PySide2.QtWidgets import QApplication, QWidget

    from app.plugins.base_state.models import TreeModel
    from app.plugins.base_state.widgets import TreeView

    application = QApplication.instance() or QApplication([])
    scheduled_callbacks = []

    class FakeTimer:
        @staticmethod
        def singleShot(_delay, callback):
            scheduled_callbacks.append(callback)

    monkeypatch.setattr('app.plugins.base_state.widgets.QTimer', FakeTimer)
    monkeypatch.setattr(TreeView, '_load_menu', lambda *_args, **_kwargs: [])

    parent = QWidget()
    view = TreeView(parent)
    refresh_calls = []
    monkeypatch.setattr(view, 'refresh', lambda: refresh_calls.append(True))

    active_model = TreeModel()
    active_model.ini_tree([_tree_data(1)])
    view.setModel(active_model)

    assert scheduled_callbacks == []
    assert refresh_calls == []

    deleted_model = TreeModel()
    deleted_model.ini_tree([_tree_data(2, deleted=True)])
    view.setModel(deleted_model)

    assert len(scheduled_callbacks) == 1
    scheduled_callbacks.pop()()
    assert refresh_calls == [True]

    view.HIDE_REMOVED_ITEMS = False
    view.setModel(deleted_model)

    assert scheduled_callbacks == []
    assert refresh_calls == [True]

    # Keep a reference for the lifetime of Qt widgets created by the test.
    assert application is not None
