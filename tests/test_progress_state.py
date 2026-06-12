from app.progress import ProgressState


def test_progress_state_is_indeterminate_without_current_or_total():
    state = ProgressState(title='Загрузка')

    assert state.is_determinate is False
    assert state.remaining is None
    assert state.percent is None


def test_progress_state_calculates_remaining_and_percent():
    state = ProgressState(title='Импорт', current=12, total=36)

    assert state.is_determinate is True
    assert state.remaining == 24
    assert state.percent == 33


def test_progress_state_clamps_completed_values():
    state = ProgressState(current=40, total=36)

    assert state.remaining == 0
    assert state.percent == 100
