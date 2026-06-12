from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')

from app.plugins.project import models


def test_workdata_import_source_uses_selected_file_and_version(monkeypatch):
    source_test = SimpleNamespace(
        _data=SimpleNamespace(id=406),
        final_version='3',
    )
    monkeypatch.setattr(
        models.sp,
        'get_product_uniskad_files',
        lambda product_id, file_type: SimpleNamespace(
            id_datafile=599, datafile_full_name='measurements.xlsx'
        ),
    )

    assert models._workdata_import_source(source_test) == (599, 3, 'measurements.xlsx')


def test_db_import_passes_exact_curve_names_and_returns_inserted_count(monkeypatch):
    calls = []
    curve_names = ['ff121423', 'ff121424']
    monkeypatch.setattr(
        models.sp,
        'import_workdata_file_curves_to_project',
        lambda *args: calls.append(args) or 82,
    )
    monkeypatch.setattr(
        models.sp,
        'get_project_data_import_stats',
        lambda project_id: SimpleNamespace(
            row_type_count=2, row_npp_count=2, column_type_count=3,
            column_npp_count=3, value_count=6,
        ),
    )

    inserted_rows = models._import_workdata_curves_db(4464, 599, 0, curve_names)

    assert inserted_rows == 82
    assert calls == [(4464, 599, 0, curve_names)]


def test_db_import_reraises_database_error_before_comparing_inserted_count(monkeypatch, caplog):
    class DatabaseRaiseError(Exception):
        pass

    database_error = DatabaseRaiseError('original database error')
    monkeypatch.setattr(models, 'RaiseError', DatabaseRaiseError)
    monkeypatch.setattr(
        models.sp, 'import_workdata_file_curves_to_project', lambda *args: database_error,
    )
    monkeypatch.setattr(
        models.sp, 'get_project_data_import_stats',
        lambda project_id: pytest.fail('validation must not run after a database error'),
    )

    with pytest.raises(DatabaseRaiseError, match='original database error'):
        models._import_workdata_curves_db(4464, 474, 0, ['A'])

    assert 'original database error' in caplog.text


def import_stats(**overrides):
    values = dict(
        row_type_count=2,
        row_npp_count=2,
        column_type_count=3,
        column_npp_count=3,
        value_count=6,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_db_import_validates_matching_nonzero_project_structure(monkeypatch):
    monkeypatch.setattr(models.sp, 'import_workdata_file_curves_to_project', lambda *args: 18)
    monkeypatch.setattr(models.sp, 'get_project_data_import_stats', lambda project_id: import_stats())

    assert models._import_workdata_curves_db(4464, 599, 0, ['A', 'B']) == 18


def test_db_import_rejects_missing_columns_with_controlled_error(monkeypatch):
    monkeypatch.setattr(models.sp, 'import_workdata_file_curves_to_project', lambda *args: 12)
    monkeypatch.setattr(
        models.sp, 'get_project_data_import_stats',
        lambda project_id: import_stats(column_type_count=0, column_npp_count=0),
    )

    with pytest.raises(models.InvalidWorkDataDbImport, match='no ProjectData columns'):
        models._import_workdata_curves_db(4464, 599, 0, ['A'])


def test_db_import_rejects_mismatched_structural_metadata(monkeypatch):
    monkeypatch.setattr(models.sp, 'import_workdata_file_curves_to_project', lambda *args: 12)
    monkeypatch.setattr(
        models.sp, 'get_project_data_import_stats',
        lambda project_id: import_stats(row_npp_count=1),
    )

    with pytest.raises(models.InvalidWorkDataDbImport, match='mismatched ProjectData metadata'):
        models._import_workdata_curves_db(4464, 599, 0, ['A'])


def test_source_resolution_cache_calls_database_once_for_duplicate_test_id(monkeypatch):
    calls = []
    source_tests = [
        SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3'),
        SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3'),
    ]
    monkeypatch.setattr(
        models.sp, 'get_product_uniskad_files',
        lambda product_id, file_type: calls.append((product_id, file_type))
        or SimpleNamespace(id_datafile=599, datafile_short_name='input.xlsx'),
    )

    cache = models._resolve_workdata_import_sources(source_tests)

    assert cache == {406: (599, 3, 'input.xlsx')}
    assert calls == [(406, 'input_excel')]
    assert models._workdata_import_source(source_tests[1], cache) == (599, 3, 'input.xlsx')
    assert calls == [(406, 'input_excel')]


def test_source_resolution_cache_preserves_failure(monkeypatch):
    calls = []
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    monkeypatch.setattr(
        models.sp, 'get_product_uniskad_files',
        lambda *args: calls.append(args) or None,
    )

    cache = models._resolve_workdata_import_sources([source_test, source_test])

    with pytest.raises(RuntimeError, match='No input Excel datafile'):
        models._workdata_import_source(source_test, cache)
    assert len(calls) == 1


def test_selected_parent_normalization_uses_selected_ids():
    root = SimpleNamespace(_data=SimpleNamespace(id_prod=1, id_up_prod=99))
    child = SimpleNamespace(_data=SimpleNamespace(id_prod=2, id_up_prod=1))
    other_root = SimpleNamespace(_data=SimpleNamespace(id_prod=3, id_up_prod=88))

    models._normalize_selected_parents([root, child, other_root], parent_id=50)

    assert root._data.id_up_prod == 50
    assert child._data.id_up_prod == 1
    assert other_root._data.id_up_prod == 50


def test_import_workdata_tests_clean_db_success_uses_only_sql_import(monkeypatch, caplog):
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    test_project = SimpleNamespace(prop_value='406', project_id=4464)
    diagnostics = models._ImportDiagnostics()
    monkeypatch.setattr(models, '_import_workdata_curves_db', lambda *args: 82)
    monkeypatch.setattr(
        models.sp, 'get_import_file_data_curves_data',
        lambda *args: pytest.fail('Python fallback must never run'),
    )
    monkeypatch.setattr(
        models.sp, 'new_project_data_array',
        lambda *args: pytest.fail('Python fallback must never run'),
    )

    counts = models._import_workdata_tests(
        [test_project], {406: source_test}, ['A'], {406: (599, 3, 'good.xlsx')}, diagnostics,
    )

    assert counts == (1, 82, [])
    assert diagnostics.values['inserted_rows'] == 82
    assert diagnostics.values['skipped_files'] == []
    diagnostics.log_summary()
    assert 'Импорт завершён успешно. Импортировано: 1. Пропущено: 0.' in caplog.text
    assert 'fallback item' not in caplog.text


def test_import_workdata_tests_skips_invalid_metadata_and_continues(monkeypatch, caplog):
    source_tests = {
        406: SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3'),
        407: SimpleNamespace(_data=SimpleNamespace(id=407), final_version='4'),
    }
    test_projects = [
        SimpleNamespace(prop_value='406', project_id=4464),
        SimpleNamespace(prop_value='407', project_id=4465),
    ]
    source_cache = {
        406: (599, 3, 'broken.xlsx'),
        407: (600, 4, 'good.xlsx'),
    }
    calls = []

    def import_curves(target_project_id, *args):
        calls.append(target_project_id)
        if target_project_id == 4464:
            raise RuntimeError(
                'WorkData import produced invalid ProjectData metadata for project 4464'
            )
        return 27

    monkeypatch.setattr(models, '_import_workdata_curves_db', import_curves)
    monkeypatch.setattr(
        models.sp, 'get_import_file_data_curves_data',
        lambda *args: pytest.fail('Python fallback must never run'),
    )
    monkeypatch.setattr(
        models.sp, 'new_project_data_array',
        lambda *args: pytest.fail('Python fallback must never run'),
    )
    diagnostics = models._ImportDiagnostics()

    counts = models._import_workdata_tests(
        test_projects, source_tests, ['A'], source_cache, diagnostics,
    )
    diagnostics.log_summary()

    skipped = counts[2]
    assert calls == [4464, 4465]
    assert counts[:2] == (2, 27)
    assert skipped == [{
        'source_test_id': 406,
        'target_project_id': 4464,
        'id_excel_file': 599,
        'file_version': 3,
        'file_name': 'broken.xlsx',
        'reason': 'Файл broken.xlsx: WorkData import produced invalid ProjectData metadata '
                  'for project 4464',
    }]
    assert diagnostics.values['inserted_rows'] == 27
    assert diagnostics.values['skipped_tests'] == [406]
    assert diagnostics.values['skipped_files'] == ['broken.xlsx']
    assert 'fallback item' not in caplog.text
    assert 'Импорт завершён частично. Импортировано: 1. Пропущено: 1.' in caplog.text
    assert 'Пропущенные файлы: broken.xlsx' in caplog.text


def test_import_workdata_tests_invalid_metadata_uses_file_id_when_name_missing(monkeypatch):
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    test_project = SimpleNamespace(prop_value='406', project_id=4464)
    monkeypatch.setattr(
        models, '_import_workdata_curves_db',
        lambda *args: (_ for _ in ()).throw(models.InvalidWorkDataDbImport('invalid metadata')),
    )

    _, _, skipped = models._import_workdata_tests(
        [test_project], {406: source_test}, ['A'], {406: (599, 3, None)},
    )

    assert skipped[0]['file_name'] == 'id_excel_file=599, version=3'
    assert 'Файл id_excel_file=599, version=3' in skipped[0]['reason']


def test_import_workdata_tests_reraises_unrelated_database_error(monkeypatch):
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    test_project = SimpleNamespace(prop_value='406', project_id=4464)
    monkeypatch.setattr(
        models, '_import_workdata_curves_db',
        lambda *args: (_ for _ in ()).throw(RuntimeError('connection lost')),
    )

    with pytest.raises(RuntimeError, match='connection lost'):
        models._import_workdata_tests(
            [test_project], {406: source_test}, ['A'], {406: (599, 3, 'input.xlsx')},
        )


def test_workdata_file_name_prefers_human_readable_datafile_name():
    datafile = SimpleNamespace(
        datafile_full_name='', full_name='', datafile_short_name='human-readable.xlsx'
    )

    assert models._workdata_file_name(datafile, 599, 3) == 'human-readable.xlsx'


def test_project_add_creates_curve_point_symbol_property_once():
    import inspect

    source = inspect.getsource(models.ProductFolderNode.add)

    assert source.count("new_prop(product_data, 'curve_point_symbol', symbol)") == 1
