from functools import lru_cache

from app.plugins.project.utils.tree import find_nodes_by_type, get_tree_root, is_node_deleted


class TestProcessor:
    @staticmethod
    @lru_cache(maxsize=None)
    def collect_tests(item):
        project_root = get_tree_root(item)
        if project_root is None:
            return {}
        tests = {}
        for test_node in find_nodes_by_type(project_root, 'test', skip_root=True):
            if TestProcessor._is_item_active(test_node) and TestProcessor._is_item_displayable(test_node):
                tests[test_node._data.project_id] = test_node
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
    def _is_item_deleted(item):
        return is_node_deleted(item)

    @staticmethod
    def _is_item_active(item):
        return not TestProcessor._is_item_deleted(item)

    @staticmethod
    def _is_item_displayable(item):
        displayable = getattr(item, 'display_as_curve', False)
        if isinstance(displayable, str):
            return displayable.lower() == 'true'
        return bool(displayable)
