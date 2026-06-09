import datetime

import pytest

pytest.importorskip('PySide2')

from PySide2.QtWidgets import QApplication

from app.plugins.project.widgets.table import ProjectTableView
from db.schemas import ProjectData


@pytest.fixture(scope='module')
def application():
    return QApplication.instance() or QApplication([])


def record(row, column, prop, value, record_id=1):
    return ProjectData({
        'id_record': record_id, 'project_id': 1, 'id_excel_file': 1,
        'file_version': 1, 'excel_param_name': row, 'param_prop_name': prop,
        'date_time_izm': column, 'zamer_n': None, 'rejim_zamer': None,
        'prop_value': value, 'deleted': False, 'npp': 0, 'id_name': 1,
        'sprav_name': None, 'id_eizm': None, 'eizm_short': None,
        'eizm_full': None,
    })


def test_project_add_remove_row_and_column_are_lazy(application):
    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    view = ProjectTableView()
    view.model().load_data([
        record('A', None, 'row_npp', '1'),
        record(None, column_1, 'column_npp', '1'),
        record('A', column_1, 'value', '1'),
    ])

    view.add_row([record('B', None, 'row_npp', '2'), record('B', column_1, 'value', '2')])
    view.add_column([record(None, column_2, 'column_npp', '2'), record('A', column_2, 'value', '3'),
                     record('B', column_2, 'value', '4')])

    assert view.ord_rows == ['A', 'B']
    assert view.ord_columns == [column_1, column_2]
    assert view.model()._items == {}
    assert view.removeRow(1)
    assert view.removeColumn(1)
    assert view.ord_rows == ['A']
    assert view.ord_columns == [column_1]


def test_project_page_header_menus_use_header_logical_indexes(application, monkeypatch):
    from types import SimpleNamespace

    from PySide2.QtCore import QPoint

    from app.plugins.project.widgets import pages

    column = datetime.datetime(2024, 1, 1)
    view = ProjectTableView()
    view.model().load_data([
        record('A', None, 'row_npp', '1'),
        record('B', None, 'row_npp', '2'),
        record(None, column, 'column_npp', '1'),
        record('A', column, 'value', '1'),
        record('B', column, 'value', '2'),
    ])
    view.setCurrentCell(0, 0)
    captured = []

    class Menu:
        def __init__(self, parent):
            pass

        def popup(self, point):
            pass

    page = SimpleNamespace(
        table=view,
        row_menu={},
        column_menu={},
        connect_triggered_funcs=captured.append,
    )
    monkeypatch.setattr(pages, 'QMenu', Menu)
    monkeypatch.setattr(pages._menu, 'init_menu', lambda *args, **kwargs: None)

    row_point = QPoint(0, view.verticalHeader().sectionViewportPosition(1) + 1)
    pages.ProjectTablePage1.show_row_menu(page, row_point)
    column_point = QPoint(view.horizontalHeader().sectionViewportPosition(0) + 1, 0)
    pages.ProjectTablePage1.show_column_menu(page, column_point)

    assert (captured[0].row(), captured[0].column()) == (1, 0)
    assert (captured[1].row(), captured[1].column()) == (0, 0)


def test_project_sparse_row_deletion_queues_existing_records_and_persists(application):
    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    row_property = record('A', None, 'type', 'row', 1)
    row_npp = record('A', None, 'row_npp', '1', 2)
    existing_cell_type = record('A', column_1, 'type', 'cell', 3)
    existing_cell_value = record('A', column_1, 'value', '1', 4)
    other_row_property = record('B', None, 'row_npp', '2', 5)
    other_cell = record('B', column_2, 'value', '2', 6)
    records = [row_property, row_npp, existing_cell_type, existing_cell_value,
               other_row_property, other_cell,
               record(None, column_1, 'column_npp', '1', 7),
               record(None, column_2, 'column_npp', '2', 8)]
    view = ProjectTableView()
    view.model().load_data(records)

    # A/column_2 is intentionally absent. Deletion must not materialize it.
    assert ('A', column_2) not in view.table
    assert view.queue_row_deletion('A') == (2, 2)
    assert ('A', column_2) not in view.table
    assert view.removeRow(0)

    assert set(view.need_update) == {row_property, row_npp, existing_cell_type, existing_cell_value}
    assert all(item.deleted for item in view.need_update)
    assert view.ord_rows == ['B']

    reloaded = ProjectTableView()
    reloaded.model().load_data([item for item in records if not item.deleted])
    assert reloaded.ord_rows == ['B']

    # A repeated/stale removal attempt is harmless and does not create records.
    assert not view.removeRow(0 + len(view.ord_rows))
    assert ('A', column_2) not in view.table


def test_project_sparse_column_deletion_queues_existing_records_and_saves(application, monkeypatch):
    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    column_property = record(None, column_1, 'type', 'column', 1)
    column_npp = record(None, column_1, 'column_npp', '1', 2)
    existing_cell = record('A', column_1, 'value', '1', 3)
    records = [column_property, column_npp, existing_cell,
               record('A', None, 'row_npp', '1', 4),
               record('B', None, 'row_npp', '2', 5),
               record(None, column_2, 'column_npp', '2', 6),
               record('B', column_2, 'value', '2', 7)]
    view = ProjectTableView()
    view.model().load_data(records)
    saved = []
    monkeypatch.setattr(view, 'SAVE_FUNCTION', lambda items: saved.extend(items) or True)

    # B/column_1 is intentionally absent. Deletion must not materialize it.
    assert ('B', column_1) not in view.table
    assert view.queue_column_deletion(column_1) == (1, 2)
    assert ('B', column_1) not in view.table
    assert view.removeColumn(0)
    assert view.update_table()

    deleted_records = {column_property, column_npp, existing_cell}
    assert all(item.deleted for item in deleted_records)
    assert set(saved) == {item.table_fit(view.TABLE_FIT) for item in deleted_records}
    assert view.need_update == []
    assert view.ord_columns == [column_2]


def test_project_page_view_delete_queues_before_removing_sparse_row(application, monkeypatch):
    from types import SimpleNamespace

    from app.plugins.project.widgets.pages import ProjectTablePage1

    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    row_property = record('A', None, 'type', 'row', 1)
    existing_cell = record('A', column_1, 'value', '1', 2)
    view = ProjectTableView()
    view.model().load_data([
        row_property, existing_cell,
        record(None, column_1, 'column_npp', '1', 3),
        record(None, column_2, 'column_npp', '2', 4),
    ])
    page = SimpleNamespace(
        table=view,
        update_formula_context=lambda: None,
        _set_formula_target=lambda item: None,
    )
    monkeypatch.setattr(
        'app.plugins.project.widgets.pages.sp.del_restore_project_data_array',
        lambda items: pytest.fail('lazy Project deletion must use the queued save path'))

    ProjectTablePage1.remove_row(page, view.model().index(0, 0))

    assert view.ord_rows == []
    assert view.need_update == [existing_cell, row_property]
    assert ('A', column_2) not in view.table
