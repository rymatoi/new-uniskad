from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')
pytest.importorskip('pyqtgraph')

from app.plugins.project.visualization.views.plot_views.mixins import plot_context_menu


class Curve:
    style_config = {'color': '#000000'}

    def name(self):
        return 'curve'


def test_customize_curve_opens_dialog_for_selected_curve(monkeypatch):
    curve = Curve()
    calls = {}

    class Dialog:
        def __init__(self, item, parent, persist_callback):
            calls.update(item=item, parent=parent, persist_callback=persist_callback)

        def exec_(self):
            return 1

    monkeypatch.setattr(plot_context_menu, 'EditLineDialog', Dialog)
    view = SimpleNamespace(curve_items=[curve], data_processor=SimpleNamespace(update_custom_curve_style=lambda item: True))

    assert plot_context_menu.PlotContextMenuMixin._open_curve_style_dialog(view, curve) is True
    assert calls['item'] is curve
    assert calls['parent'] is view


def test_customize_curve_does_not_open_for_missing_curve(monkeypatch):
    monkeypatch.setattr(plot_context_menu, 'EditLineDialog', lambda *args, **kwargs: pytest.fail('dialog opened'))
    view = SimpleNamespace(curve_items=[], data_processor=SimpleNamespace())

    assert plot_context_menu.PlotContextMenuMixin._open_curve_style_dialog(view, Curve()) is False
