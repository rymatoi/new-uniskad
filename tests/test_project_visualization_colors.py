import os

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')
pytest.importorskip('pyqtgraph')

from PySide2.QtGui import QColor

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets import colors
from app.plugins.project.visualization.widgets.colors import safe_color
from app.plugins.project.visualization.widgets.curve import CurveItem
from app.plugins.project.visualization.widgets.epure import EpureItem


def test_dark_yellow_is_supported():
    color = EpureItem._ensure_opaque_color('DarkYellow')

    assert color.isValid()
    assert color.name() == '#808000'
    assert color.alpha() == 255


def test_curve_uses_same_safe_named_color_conversion():
    color = CurveItem._convert_color('DarkYellow')

    assert color.isValid()
    assert color.name() == '#808000'


def test_fallback_warning_is_logged_only_once(monkeypatch):
    warnings = []
    colors._warned_fallback_values.clear()
    monkeypatch.setattr(colors.logger, 'warning', lambda *args: warnings.append(args))

    safe_color('bad-color-for-warning-test', '#000000')
    safe_color('bad-color-for-warning-test', '#000000')

    assert len(warnings) == 1


@pytest.mark.parametrize('value', ['not-a-real-color', object(), '', None])
def test_unsupported_or_empty_epure_color_uses_valid_opaque_fallback(value):
    color = EpureItem._ensure_opaque_color(value)

    assert color.isValid()
    assert color.name() == GraphConstants.DEFAULT_STYLE['color']
    assert color.alpha() == 255


def test_valid_color_is_preserved_and_made_opaque():
    color = EpureItem._ensure_opaque_color(QColor(12, 34, 56, 20))

    assert color.getRgb() == (12, 34, 56, 255)


def test_transparent_curve_color_remains_disabled():
    assert safe_color('transparent', '#000000', allow_transparent=True) is None
