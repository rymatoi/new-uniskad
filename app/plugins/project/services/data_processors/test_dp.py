from functools import lru_cache


class TestProcessor:
    @staticmethod
    @lru_cache(maxsize=None)
    def collect_tests(item):
        node = item
        visited_ids = set()
        while node is not None and id(node) not in visited_ids:
            visited_ids.add(id(node))
            parent_getter = getattr(node, 'parent', None)
            if parent_getter is None:
                break
            parent = parent_getter()
            if parent is None:
                break
            internal_type_getter = getattr(parent, 'internal_type', None)
            if internal_type_getter is not None and internal_type_getter() == 'product_folder':
                return TestProcessor._inspect_children(parent)

            children = getattr(parent, 'children', []) or []
            for child in children:
                internal_type_getter = getattr(child, 'internal_type', None)
                if internal_type_getter is None:
                    continue
                if internal_type_getter() == 'product_folder':
                    return TestProcessor._inspect_children(child)
            node = parent
        return {}

    @staticmethod
    def get_item_style(item):  # TODO надо будет учитывать настройки отображений по условиям
        symbol = item.curve_point_symbol
        if isinstance(symbol, str) and symbol.lower() in {'none', ''}:
            symbol = None

        symbol_color = getattr(item, 'curve_symbol_color', item.curve_color)
        if isinstance(symbol_color, str) and symbol_color.lower() in {'none', ''}:
            symbol_color = item.curve_color
        elif symbol_color is None:
            symbol_color = item.curve_color

        fill_color = getattr(item, 'curve_symbol_fill_color', symbol_color)
        if isinstance(fill_color, str) and fill_color.lower() in {'none', ''}:
            fill_color = symbol_color
        elif fill_color is None:
            fill_color = symbol_color

        return {
            'color': item.curve_color,
            'width': int(item.curve_width),
            'line_style': int(item.curve_line_style),
            'symbol_size': int(item.curve_point_size),
            'symbol': symbol,
            'symbol_color': symbol_color,
            'fill_color': fill_color,
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
