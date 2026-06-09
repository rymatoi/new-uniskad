import os
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QWidget

from app.plugins.project.widgets.tabs import TestTableTab as ProjectTestTableTab


class FakeIndex(QModelIndex):
    def __init__(self, item):
        super().__init__()
        self._item = item

    def internalPointer(self):
        return self._item


@pytest.fixture
def application():
    return QApplication.instance() or QApplication([])


def make_item(project_id=101):
    return SimpleNamespace(
        _data=SimpleNamespace(project_id=project_id),
        data=lambda: 'Project table',
    )


def test_project_table_tab_loads_once_and_reuses_page(application, monkeypatch):
    calls = []
    page = QWidget()
    parent = QWidget()
    parent._restoring_tabs = False
    monkeypatch.setattr(
        'app.plugins.project.widgets.tabs.sp.get_project_data',
        lambda project_id: calls.append(project_id) or ['cell'],
    )
    monkeypatch.setattr(
        'app.plugins.project.widgets.tabs.ProjectTablePage1',
        lambda cells, item, tab, main_window: page,
    )

    tab = ProjectTestTableTab(FakeIndex(make_item()), parent)

    assert not tab._loaded
    assert calls == []

    assert tab.ensure_loaded() is page
    assert tab.ensure_loaded() is page
    assert calls == [101]


def test_project_table_refresh_is_deferred_before_first_load(application, monkeypatch):
    calls = []
    parent = QWidget()
    parent._restoring_tabs = False
    monkeypatch.setattr(
        'app.plugins.project.widgets.tabs.sp.get_project_data',
        lambda project_id: calls.append(project_id) or [],
    )

    tab = ProjectTestTableTab(FakeIndex(make_item()), parent)
    tab.refresh(FakeIndex(make_item()))

    assert tab._refresh_pending
    assert calls == []
