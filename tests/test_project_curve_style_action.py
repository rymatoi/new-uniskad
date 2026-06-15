from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')
pytest.importorskip('pyqtgraph')

from app.plugins.project.visualization.views.plot_views.mixins import plot_context_menu
from app.plugins.project.dialogs import edit_line


class Curve:
    style_config = {'color': '#000000'}

    def name(self):
        return 'curve'


def test_edit_line_dialog_forwards_parent_without_conflicting_with_flags(monkeypatch):
    parent = object()
    calls = {}

    class StopInitialization(Exception):
        pass

    def base_dialog_init(self, *args, **kwargs):
        calls.update(args=args, kwargs=kwargs)
        raise StopInitialization

    monkeypatch.setattr(edit_line.BaseDialog, '__init__', base_dialog_init)

    with pytest.raises(StopInitialization):
        edit_line.EditLineDialog(Curve(), parent=parent)

    assert calls == {'args': (), 'kwargs': {'flags': None, 'parent': parent}}


def test_edit_line_dialog_has_point_symbols():
    assert edit_line.EditLineDialog.POINT_SYMBOLS
    assert ('o', 'Круг') in edit_line.EditLineDialog.POINT_SYMBOLS


def test_edit_line_dialog_falls_back_for_unknown_saved_style():
    items = [('known', 'Known')]

    assert edit_line.EditLineDialog._index_for_value(items, 'missing') == 0
    assert edit_line.EditLineDialog._index_for_value(items, 'missing', 3) == 3


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
