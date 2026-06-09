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


def test_restored_project_tabs_stay_lazy_until_active_tab_is_loaded(application, monkeypatch):
    calls = []
    page = QWidget()
    parent = QWidget()
    parent._restoring_tabs = True
    monkeypatch.setattr(
        'app.plugins.project.widgets.tabs.sp.get_project_data',
        lambda project_id: calls.append(project_id) or ['cell'],
    )
    monkeypatch.setattr(
        'app.plugins.project.widgets.tabs.ProjectTablePage1',
        lambda cells, item, tab, main_window: page,
    )

    inactive_tab = ProjectTestTableTab(FakeIndex(make_item(101)), parent)
    active_tab = ProjectTestTableTab(FakeIndex(make_item(202)), parent)
    inactive_tab._load_when_visible(True)
    active_tab._load_when_visible(True)

    assert calls == []
    assert not inactive_tab._loaded
    assert not active_tab._loaded

    active_tab.ensure_loaded()

    assert calls == [202]
    assert not inactive_tab._loaded
    assert active_tab._loaded
