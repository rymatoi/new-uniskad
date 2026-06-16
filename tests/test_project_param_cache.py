from app.plugins.project import utils_


def setup_function():
    utils_.clear_project_params()


def test_project_params_are_cached_and_force_reload(monkeypatch):
    calls = []
    monkeypatch.setattr(utils_.sp, 'get_project_param_names', lambda project_id: calls.append(project_id) or [str(len(calls))])
    assert list(utils_.get_project_params(1)) == ['1']
    assert list(utils_.get_project_params(1)) == ['1']
    assert list(utils_.get_project_params(1, force_reload=True)) == ['2']
    assert calls == [1, 1]


def test_clear_only_one_project_and_values_cache(monkeypatch):
    param_calls = []
    value_calls = []
    monkeypatch.setattr(utils_.sp, 'get_project_param_names', lambda project_id: param_calls.append(project_id) or [])
    monkeypatch.setattr(utils_.sp, 'get_params_values', lambda names, project_id: value_calls.append((names, project_id)) or [project_id])
    utils_.get_project_params(1); utils_.get_project_params(2)
    assert utils_.get_param_values(1, 'x') == [1]
    assert utils_.get_param_values(1, 'x') == [1]
    utils_.clear_project_params(1)
    utils_.get_project_params(1); utils_.get_project_params(2)
    utils_.get_param_values(1, 'x')
    assert param_calls == [1, 2, 1]
    assert value_calls == [(['x'], 1), (['x'], 1)]


def test_empty_param_values_are_cached(monkeypatch):
    value_calls = []
    monkeypatch.setattr(
        utils_.sp,
        'get_params_values',
        lambda names, project_id: value_calls.append((names, project_id)) or [],
    )

    assert utils_.get_param_values(1, 'empty') == []
    assert utils_.get_param_values(1, 'empty') == []
    assert value_calls == [(['empty'], 1)]


def test_blank_param_name_skips_db(monkeypatch):
    value_calls = []
    monkeypatch.setattr(
        utils_.sp,
        'get_params_values',
        lambda names, project_id: value_calls.append((names, project_id)) or ['unexpected'],
    )

    assert utils_.get_param_values(1, None) == []
    assert utils_.get_param_values(1, '') == []
    assert value_calls == []
