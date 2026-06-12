import pytest

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
