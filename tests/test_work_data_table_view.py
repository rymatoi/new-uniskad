import datetime

import pytest

pytest.importorskip('PySide2')

from openpyxl import load_workbook
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

from app.plugins.work_data.widgets.table import WorkDataTableView
from db.schemas import ImportFileData


@pytest.fixture(scope='module')
def application():
    return QApplication.instance() or QApplication([])


def record(row, column, prop, value, record_id=1):
    return ImportFileData({
        'id_record': record_id,
        'is_secret': False,
        'id_excel_file': 1,
        'file_version': 1,
        'excel_param_name': row,
        'param_prop_name': prop,
        'date_time_izm': column,
        'zamer_n': None,
        'rejim_zamer': None,
        'prop_value': value,
        'deleted': False,
        'id_name': 1,
        'sprav_name': None,
        'accuracy': 2,
        'id_eizm': None,
        'eizm_short': None,
        'eizm_full': None,
    })


def sample_records():
    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    return [
        record('B', None, 'row_npp', '2'),
        record('B', None, 'accuracy', '1'),
        record('A', None, 'row_npp', '1'),
        record('A', None, 'accuracy', '2'),
        record(None, column_2, 'column_npp', '2'),
        record(None, column_1, 'column_npp', '1'),
        record('A', column_1, 'value', '1.25'),
        record('A', column_1, 'formula', ''),
        record('A', column_2, 'value', '2'),
        record('B', column_1, 'value', '3'),
        record('B', column_2, 'value', '4'),
    ]


def make_view(application):
    view = WorkDataTableView()
    view.model().load_data(sample_records())
    return view


def test_model_lookup_and_compatibility_indexes_are_ordered_and_lazy(application):
    view = make_view(application)
    model = view.model()

    assert model.ord_rows == ['A', 'B']
    assert model.ord_columns == [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 2)]
    assert model._items == {}

    index = model.index(0, 0)
    item = view.itemFromIndex(index)
    assert item.key == ('A', datetime.datetime(2024, 1, 1))
    assert view.indexFromItem(item) == index
    assert len(model._items) == 1
    assert model.data(index, Qt.DisplayRole) == '1.25'


def test_set_data_updates_cell_and_save_queue(application):
    view = make_view(application)
    index = view.model().index(0, 0)

    assert view.model().setData(index, '=1+1', Qt.EditRole)
    assert view.table[('A', datetime.datetime(2024, 1, 1))]['formula'].prop_value == '=1+1'
    assert view.need_update[-1].param_prop_name == 'formula'


def test_export_uses_model_values_without_eager_items(application, tmp_path):
    view = make_view(application)
    output = tmp_path / 'work-data.xlsx'

    view.export(str(output))
    worksheet = load_workbook(output).active

    assert worksheet.cell(1, 1).value == 'A'
    assert worksheet.cell(1, 2).value == 1.25
    assert view.model()._items == {}


def test_work_data_view_rejects_structural_operations_without_mutation(application):
    view = make_view(application)
    rows = list(view.ord_rows)
    columns = list(view.ord_columns)
    table_keys = set(view.table)

    assert not view.update_ord_row('Renamed A', 'A')
    assert not view.add_row([record('New', None, 'row_npp', '3')])
    assert not view.add_column([record(None, datetime.datetime(2024, 1, 3), 'column_npp', '3')])
    assert not view.queue_row_deletion('A')
    assert not view.queue_column_deletion(columns[0])
    assert not view.removeRow(0)
    assert not view.removeColumn(0)

    assert view.ord_rows == rows
    assert view.ord_columns == columns
    assert set(view.table) == table_keys
    assert view.need_update == []


def test_work_data_legacy_table_rejects_structural_operations(application):
    from app.plugins.work_data.widgets.table import WorkDataTableWidget

    table = WorkDataTableWidget(None, None)
    table.load_table(sample_records())
    rows = list(table.ord_rows)
    columns = list(table.ord_columns)

    assert not table.update_ord_row('Renamed A', 'A')
    assert not table.add_row([record('New', None, 'row_npp', '3')])
    assert not table.add_column([record(None, datetime.datetime(2024, 1, 3), 'column_npp', '3')])
    assert not table.removeRow(0)
    assert not table.removeColumn(0)
    assert table.ord_rows == rows
    assert table.ord_columns == columns


def test_missing_row_property_does_not_mutate_type_record(application, monkeypatch):
    from app.plugins.work_data.widgets.pages import WorkDataTablePage1

    type_record = record('A', None, 'type', 'row')
    table = type('Table', (), {
        'rows': {('A', None): {'type': type_record}},
        'update_row_obj': lambda self, *args: None,
    })()
    page = type('Page', (), {'table': table})()
    monkeypatch.setattr('app.plugins.work_data.widgets.pages.sp.new_upd_excel_data_record',
                        lambda value: value)

    WorkDataTablePage1.update_row_prop(page, 'A', 'row_formula', '=1+1')

    assert type_record.param_prop_name == 'type'
    assert type_record.prop_value == 'row'


def test_qtablewidget_compatibility_counts_and_selected_ranges(application):
    from PySide2.QtCore import QItemSelection, QItemSelectionModel

    view = make_view(application)
    selection = QItemSelection(view.model().index(0, 0), view.model().index(1, 1))
    view.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)

    assert view.rowCount() == 2
    assert view.columnCount() == 2
    ranges = view.selectedRanges()
    assert len(ranges) == 1
    assert (ranges[0].topRow(), ranges[0].leftColumn(),
            ranges[0].bottomRow(), ranges[0].rightColumn()) == (0, 0, 1, 1)


def test_set_data_converts_non_string_edit_values_and_preserves_formulas(application):
    view = make_view(application)
    index = view.model().index(0, 0)
    formula = view.table[('A', datetime.datetime(2024, 1, 1))]['formula']

    assert view.model().setData(index, 42, Qt.EditRole)
    assert formula.prop_value == '42'
    assert view.model().setData(index, None, Qt.EditRole)
    assert formula.prop_value == ''


def sparse_records():
    column_1 = datetime.datetime(2024, 1, 1)
    column_2 = datetime.datetime(2024, 1, 2)
    return [
        record('A', None, 'row_npp', '1'),
        record('A', None, 'accuracy', '2'),
        record(None, column_1, 'column_npp', '1'),
        record(None, column_2, 'column_npp', '2'),
        record('A', column_1, 'type', 'cell'),
        record('A', column_1, 'value', '1'),
    ]


def test_displaying_missing_sparse_intersection_is_empty_and_non_mutating(application):
    view = WorkDataTableView()
    view.model().load_data(sparse_records())
    key = ('A', datetime.datetime(2024, 1, 2))
    index = view.model().index(0, 1)

    assert key not in view.table
    assert view.model().data(index, Qt.DisplayRole) == ''
    assert view.model().data(index, Qt.EditRole) == ''
    assert view.itemFromIndex(index) is None
    assert key not in view.table
    assert view.need_update == []


def test_editing_missing_sparse_intersection_creates_complete_queued_cell(application):
    view = WorkDataTableView()
    view.model().load_data(sparse_records())
    key = ('A', datetime.datetime(2024, 1, 2))
    index = view.model().index(0, 1)

    assert view.model().setData(index, '=1+1', Qt.EditRole)

    assert {'type', 'value', 'formula', 'cformula'} <= set(view.table[key])
    assert view.table[key]['type'].prop_value == 'cell'
    assert view.table[key]['value'].prop_value == '0'
    assert view.table[key]['cformula'].prop_value == '2'
    assert {'type', 'value', 'formula', 'cformula'} <= {
        item.param_prop_name for item in view.need_update
    }
    assert view.table[key]['type'] is not view.table[key]['value']


def test_formula_record_without_value_safely_displays_and_heals_on_write(application):
    column = datetime.datetime(2024, 1, 1)
    cformula = record('A', column, 'cformula', '')
    view = WorkDataTableView()
    view.model().load_data([
        record('A', None, 'row_npp', '1'),
        record(None, column, 'column_npp', '1'),
        record('A', column, 'formula', '=1+1'),
        cformula,
    ])
    index = view.model().index(0, 0)

    assert view.model().data(index, Qt.DisplayRole) == ''
    assert 'value' not in view.table[('A', column)]
    assert view.model().setData(index, '=2+2', Qt.EditRole)
    assert {'type', 'value', 'formula', 'cformula'} <= set(view.table[('A', column)])


def test_row_formula_materializes_missing_sparse_cell(application, monkeypatch):
    from types import SimpleNamespace

    from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog
    from dialogs.base import BaseDialog

    view = WorkDataTableView()
    view.model().load_data(sparse_records())
    missing_key = ('A', datetime.datetime(2024, 1, 2))

    def update_row_prop(row, prop, value):
        view.update_row_obj(row, prop, record(row, None, prop, str(value), None))

    page = SimpleNamespace(update_row_prop=update_row_prop, refresh_formula_result=lambda: None)
    dialog = RowSettingsDialog.__new__(RowSettingsDialog)
    BaseDialog.__init__(dialog)
    dialog.table_page = page
    dialog.table = view
    dialog.item = view.item(0, 0)
    dialog.row = 'A'
    dialog.formula_edit = SimpleNamespace(text=lambda: '=COLUMN()')
    dialog.ui = SimpleNamespace(
        nameLineEdit=SimpleNamespace(text=lambda: 'A'),
        accuracySpinBox=SimpleNamespace(value=lambda: 2),
        fromComboBox_2=SimpleNamespace(currentText=lambda: 'Пусто'),
        toComboBox_2=SimpleNamespace(currentText=lambda: 'Пусто'),
    )
    monkeypatch.setattr(BaseDialog, 'accept', lambda self: None)

    RowSettingsDialog.accept(dialog)

    assert {'type', 'value', 'cformula'} <= set(view.table[missing_key])
    assert view.table[missing_key]['cformula'].prop_value == '2'
    assert {'type', 'value', 'cformula'} <= {item.param_prop_name for item in view.need_update}


def test_work_data_page_rejects_structural_properties_without_db_write(application, monkeypatch):
    from types import SimpleNamespace

    from app.plugins.work_data.widgets.pages import WorkDataTablePage1

    calls = []
    page = SimpleNamespace(
        table=SimpleNamespace(rows={('A', None): {'row_npp': record('A', None, 'row_npp', '1')}},
                              columns={}, update_row_obj=lambda *args: None),
        STRUCTURAL_ROW_PROPERTIES=WorkDataTablePage1.STRUCTURAL_ROW_PROPERTIES,
        STRUCTURAL_COLUMN_PROPERTIES=WorkDataTablePage1.STRUCTURAL_COLUMN_PROPERTIES,
        _reject_structural_edit=lambda: False,
        _property_template=WorkDataTablePage1._property_template,
    )
    monkeypatch.setattr('app.plugins.work_data.widgets.pages.sp.new_upd_excel_data_record',
                        lambda value: calls.append(value) or True)

    assert not WorkDataTablePage1.update_row_prop(page, 'A', 'name', 'Renamed A')
    assert calls == []


def test_work_data_page_clones_allowed_property_without_type_metadata(application, monkeypatch):
    from types import SimpleNamespace

    from app.plugins.work_data.widgets.pages import WorkDataTablePage1

    row_npp = record('A', None, 'row_npp', '1')
    updated = []
    page = SimpleNamespace(
        table=SimpleNamespace(rows={('A', None): {'row_npp': row_npp}}, columns={},
                              update_row_obj=lambda *args: updated.append(args)),
        STRUCTURAL_ROW_PROPERTIES=WorkDataTablePage1.STRUCTURAL_ROW_PROPERTIES,
        _reject_structural_edit=lambda: False,
        _property_template=WorkDataTablePage1._property_template,
    )
    monkeypatch.setattr('app.plugins.work_data.widgets.pages.sp.new_upd_excel_data_record',
                        lambda value: True)

    assert WorkDataTablePage1.update_row_prop(page, 'A', 'accuracy', 3)
    assert updated[0][1] == 'accuracy'
    assert row_npp.param_prop_name == 'row_npp'
    assert row_npp.prop_value == '1'


def test_row_settings_does_not_rename_when_structural_editing_is_disabled(application):
    from types import SimpleNamespace

    from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog

    updates = []
    dialog = RowSettingsDialog.__new__(RowSettingsDialog)
    dialog.structural_editing_enabled = False
    dialog.row = 'A'
    dialog.table_page = SimpleNamespace(
        structural_editing_enabled=False,
        update_row_prop=lambda *args: updates.append(args),
    )
    dialog.table = SimpleNamespace(
        get_row_prop=lambda *args: '',
        update_ord_row=lambda *args: updates.append(args),
    )
    dialog.ui = SimpleNamespace(nameLineEdit=SimpleNamespace(text=lambda: 'Renamed A'))

    assert not dialog.update_name('Renamed A')
    assert updates == []


def test_table_font_role_inherits_global_without_explicit_format(application):
    view = make_view(application)
    index = view.model().index(0, 0)

    assert view.model().data(index, Qt.FontRole) is None


def test_table_font_role_preserves_cell_row_column_format_precedence(application):
    column = datetime.datetime(2024, 1, 1)
    view = WorkDataTableView()
    view.model().load_data([
        record('A', None, 'row_npp', '1'),
        record('A', None, 'font_size', '16'),
        record(None, column, 'column_npp', '1'),
        record(None, column, 'font_name', 'DejaVu Serif'),
        record('A', column, 'value', '1'),
        record('A', column, 'font_size', '19'),
        record('A', column, 'font_bold', 'True'),
    ])

    font = view.model().data(view.model().index(0, 0), Qt.FontRole)

    assert font.family() == 'DejaVu Serif'
    assert font.pointSize() == 19
    assert font.bold()
