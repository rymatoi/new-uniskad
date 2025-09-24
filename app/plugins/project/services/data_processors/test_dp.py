from functools import lru_cache

from app.plugins.project import utils


class TestProcessor:
    @staticmethod
    @lru_cache(maxsize=None)
    def collect_tests(item):
        parent = item.parent().parent()
        tests = {}
        for test in utils.collect_nodes_by_internal_type(parent, {'test'}):
            if TestProcessor._is_item_displayable(test):
                tests[test._data.project_id] = test
        return tests

    @staticmethod
    def get_item_style(item):  # TODO надо будет учитывать настройки отображений по условиям
        return {
            'color': item.curve_color,
            'width': int(item.curve_width),
            'line_style': int(item.curve_line_style),
            'symbol_size': int(item.curve_point_size),
            'symbol': item.curve_point_symbol,
            'fill_color': item.curve_symbol_fill_color,
            'name': item.curve_name if item.curve_name else item.name
        }

    @staticmethod
    def _is_item_displayable(item):
        displayable = getattr(item, 'display_as_curve', False)
        if isinstance(displayable, str):
            return displayable.lower() == 'true'
        return bool(displayable)
