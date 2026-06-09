from types import SimpleNamespace

from app.menu_service import MenuService


def test_repeated_menu_requests_load_once_and_return_independent_lists():
    calls = []
    menu_entry = SimpleNamespace(name='_open')

    def loader(mode, location):
        calls.append((mode, location))
        return [menu_entry]

    service = MenuService(loader)

    first = service.get_menu('any', 'table')
    first.append(SimpleNamespace(name='_local_only'))
    second = service.get_menu('any', 'table')

    assert calls == [('any', 'table')]
    assert second == [menu_entry]
    assert first is not second


def test_different_menu_keys_are_cached_independently():
    calls = []

    def loader(mode, location):
        calls.append((mode, location))
        return [SimpleNamespace(name=f'{mode}_{location}')]

    service = MenuService(loader)

    service.get_menu('any', 'table')
    service.get_menu('any', 'table_row')
    service.get_menu('any', 'table')

    assert calls == [('any', 'table'), ('any', 'table_row')]


def test_clear_for_authorization_or_role_change_forces_reload():
    calls = []

    def loader(mode, location):
        calls.append((mode, location))
        return [SimpleNamespace(name='_open')]

    service = MenuService(loader)
    service.get_menu('any', 'main_menu')

    service.clear('authorization updated')
    service.get_menu('any', 'main_menu')
    service.clear('active role changed')
    service.get_menu('any', 'main_menu')

    assert calls == [
        ('any', 'main_menu'),
        ('any', 'main_menu'),
        ('any', 'main_menu'),
    ]


def test_invalid_results_do_not_poison_cache():
    invalid_result = object()
    results = [None, invalid_result, [SimpleNamespace(name='_open')]]

    service = MenuService(lambda mode, location: results.pop(0))

    assert service.get_menu('any', 'table') is None
    assert service.get_menu('any', 'table') is invalid_result
    assert len(service.get_menu('any', 'table')) == 1
    assert len(service.get_menu('any', 'table')) == 1
    assert results == []
