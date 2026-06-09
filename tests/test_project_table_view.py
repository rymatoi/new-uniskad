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
