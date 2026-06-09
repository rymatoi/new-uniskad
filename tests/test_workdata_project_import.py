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

    inserted_rows = models._import_workdata_curves_db(4464, 599, 0, curve_names)

    assert inserted_rows == 82
    assert calls == [(4464, 599, 0, curve_names)]
