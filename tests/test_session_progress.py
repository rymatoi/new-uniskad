from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')

from db._session import Session
from app.progress import ProgressState


class FakeSignal:
    def __init__(self):
        self.values = []

    def emit(self, value):
        self.values.append(value)


def make_session():
    session = Session.__new__(Session)
    session.main_window = object()
    session._progress_emitter = SimpleNamespace(progress=FakeSignal())
    session._last_progress_message = None
    session._progress_state = None
    session._progress_started_at = None
    return session


def test_legacy_string_update_is_converted_to_progress_state():
    session = make_session()

    state = session.update_loading_bar('Загрузка проекта')

    assert state == ProgressState(title='Загрузка проекта')
    assert session._progress_emitter.progress.values == [state]


def test_legacy_string_update_preserves_active_batch_counts():
    session = make_session()
    session.begin_progress('Импорт WorkData', total=36)
    session.update_progress(current=12)

    state = session.update_loading_bar('Импорт файла')

    assert state.title == 'Импорт WorkData'
    assert state.message == 'Импорт файла'
    assert state.current == 12
    assert state.total == 36


def test_progress_context_always_ends_after_exception():
    session = make_session()

    with pytest.raises(RuntimeError, match='failed'):
        with session.progress('Импорт WorkData', total=2) as progress:
            progress.update(current=1, detail='Файл: first.xlsx')
            raise RuntimeError('failed')

    assert session.has_active_progress is False
    assert session._progress_state is None
    assert session._progress_emitter.progress.values[-1] is None
