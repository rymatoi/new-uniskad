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
        lambda product_id, file_type: SimpleNamespace(id_datafile=599),
    )

    assert models._workdata_import_source(source_test) == (599, 3)


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
        or SimpleNamespace(id_datafile=599),
    )

    cache = models._resolve_workdata_import_sources(source_tests)

    assert cache == {406: (599, 3)}
    assert calls == [(406, 'input_excel')]
    assert models._workdata_import_source(source_tests[1], cache) == (599, 3)
    assert calls == [(406, 'input_excel')]


def test_source_resolution_cache_preserves_failure_for_fallback(monkeypatch):
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


def test_import_workdata_tests_clean_db_success_avoids_fallback(monkeypatch):
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    test_project = SimpleNamespace(prop_value='406', project_id=4464)
    monkeypatch.setattr(models, '_import_workdata_curves_db', lambda *args: 82)
    monkeypatch.setattr(
        models.sp, 'get_import_file_data_curves_data',
        lambda *args: pytest.fail('fallback must not run after DB success'),
    )

    counts = models._import_workdata_tests(
        [test_project], {406: source_test}, ['A'], None, {406: (599, 3)},
    )

    assert counts == (1, 82, 0)


def test_import_workdata_tests_db_failure_uses_fallback(monkeypatch):
    source_test = SimpleNamespace(_data=SimpleNamespace(id=406), final_version='3')
    test_project = SimpleNamespace(prop_value='406', project_id=4464)
    param = SimpleNamespace(
        prop_name='value', prop_value='1', excel_param_name='A', is_secret=False,
        table_fit=lambda table: (2, 'value'),
    )
    monkeypatch.setattr(
        models, '_import_workdata_curves_db', lambda *args: (_ for _ in ()).throw(RuntimeError('db failed')),
    )
    monkeypatch.setattr(models.sp, 'get_import_file_data_curves_data', lambda *args: [param])
    monkeypatch.setattr(models.sp, 'new_project_data_array', lambda rows: rows)

    counts = models._import_workdata_tests(
        [test_project], {406: source_test}, ['A'], None, {406: (599, 3)},
    )

    assert counts == (1, 0, 1)
    assert param.project_id == 4464


def test_project_add_creates_curve_point_symbol_property_once():
    import inspect

    source = inspect.getsource(models.ProductFolderNode.add)

    assert source.count("new_prop(product_data, 'curve_point_symbol', symbol)") == 1
