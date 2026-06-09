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
