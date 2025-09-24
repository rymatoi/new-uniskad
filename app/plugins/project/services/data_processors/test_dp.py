from functools import lru_cache


class TestProcessor:
    @staticmethod
    @lru_cache(maxsize=None)
    def collect_tests(item):
        root = item.parent()
        if root:
            root = root.parent()
        if not root:
            return {}
        test_folder = root.find_child_by_internal_type('product_folder')
        if not test_folder:
            return {}
        return TestProcessor._inspect_children(test_folder)

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
    def _inspect_children(root, parent_deleted=False):
        test_dict = {}
        for child in root.children:
            if child.internal_type() == 'test':
                if not parent_deleted and TestProcessor._is_item_active(
                        child) and TestProcessor._is_item_displayable(child):
                    test_dict[child._data.project_id] = child
            else:
                child_deleted = parent_deleted or TestProcessor._is_item_deleted(child)
                test_dict.update(TestProcessor._inspect_children(child, child_deleted))
        return test_dict

    @staticmethod
    def _is_item_deleted(item):
        deleted = getattr(item._data, 'deleted', False)
        if isinstance(deleted, str):
            return deleted.lower() == 'true'
        return bool(deleted)

    @staticmethod
    def _is_item_active(item):
        return not TestProcessor._is_item_deleted(item)

    @staticmethod
    def _is_item_displayable(item):
        displayable = getattr(item, 'display_as_curve', False)
        if isinstance(displayable, str):
            return displayable.lower() == 'true'
        return bool(displayable)
