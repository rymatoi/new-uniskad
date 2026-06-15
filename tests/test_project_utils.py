import pytest

pytest.importorskip('PySide2')


def test_get_next_default_combination_is_public():
    from app.plugins.project import utils

    line_style, color, symbol = utils.get_next_default_combination(0)

    assert line_style
    assert isinstance(color, str) and color
    assert isinstance(symbol, str) and symbol
