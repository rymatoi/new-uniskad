import json
from types import SimpleNamespace

import pytest

pytest.importorskip('PySide2')
pytest.importorskip('pyqtgraph')

from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.plot_dp import PlotProcessor


def make_processor(curves):
    processor = PlotProcessor.__new__(PlotProcessor)
    processor.other_data = curves
    processor.plot_data = {}
    processor.test_nodes = {}
    return processor


def test_missing_test_id_does_not_raise():
    processor = make_processor([SimpleNamespace(id=1, values=json.dumps({'type': 'manual', 'points': [[1, 2]]}))])

    assert list(processor.get_custom_curves()) == []


def test_string_test_id_is_normalized_for_manual_curve():
    curve = SimpleNamespace(id=2, values=json.dumps({'type': 'manual', 'test_id': '42', 'points': [[1, 2]]}))

    result = list(make_processor([curve]).get_custom_curves())

    assert result[0][0] == 42


def test_invalid_json_does_not_raise():
    assert list(make_processor([SimpleNamespace(id=3, values='{bad')]).get_custom_curves()) == []


def test_valid_manual_curve_is_processed_as_before():
    curve = SimpleNamespace(id=4, values={'type': 'manual', 'test_id': 7, 'name': 'Custom', 'points': [[1, 2], [3, 4]]})

    test_id, x, y, style = list(make_processor([curve]).get_custom_curves())[0]

    assert (test_id, x, y, style['name'], style['custom_curve_id']) == (7, [1.0, 3.0], [2.0, 4.0], 'Custom', 4)


def test_legacy_curve_model_test_id_is_used():
    assert ItemProcessor.get_custom_curve_test_id({}, SimpleNamespace(test_id='9')) == 9


def test_generated_custom_curve_uses_stored_parameters_without_losing_metadata(monkeypatch):
    values = {
        'type': 'polynomial', 'degree': 2, 'test_id': 7, 'name': 'Approx',
        'x_param': 'temperature', 'y_param': 'pressure', 'extra': 'kept',
    }
    curve = SimpleNamespace(id=5, values=values)
    processor = make_processor([curve])
    processor.load_plot_data = lambda x, y: {'selected': (x, y)}
    monkeypatch.setattr(
        ItemProcessor, 'get_other_data',
        lambda plot_data, curves, nodes: iter([(7, [1], [2], {'name': 'Approx'})]),
    )

    _, _, _, style = list(processor.get_custom_curves())[0]

    assert style['custom_curve_id'] == 5
    assert (style['x_param'], style['y_param']) == ('temperature', 'pressure')
    assert values['extra'] == 'kept'
