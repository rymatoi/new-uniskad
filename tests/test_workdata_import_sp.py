import pytest

pytest.importorskip('asyncpg')

from db import sp


def test_import_workdata_wrapper_calls_database_function(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sp.session,
        'call',
        lambda *args: calls.append(args) or 82,
    )

    result = sp.import_workdata_file_curves_to_project.__wrapped__(
        4464, 599, 0, ['ff121423', 'ff121424']
    )

    assert result == 82
    assert calls == [(
        'import_workdata_file_curves_to_project',
        4464,
        599,
        0,
        ['ff121423', 'ff121424'],
    )]
