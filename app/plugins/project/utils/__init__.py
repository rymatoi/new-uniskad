from collections import deque
from typing import Iterable, List, Union


def _to_bool(value) -> bool:
    """Convert database boolean representations to bool."""

    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)


def is_node_deleted(node) -> bool:
    """Check whether the provided tree node is marked as deleted."""

    data = getattr(node, '_data', None)
    deleted = getattr(data, 'deleted', False)
    return _to_bool(deleted)


def iter_project_nodes(root, include_self: bool = False):
    """Yield active nodes in the project tree starting from ``root``.

    The traversal respects the ``deleted`` flag of every node, skipping nodes
    that are marked as deleted as well as their descendants. By default the
    ``root`` node itself is excluded from the result.
    """

    queue = deque([(root, False)])
    while queue:
        node, ancestors_deleted = queue.popleft()
        node_deleted = ancestors_deleted or is_node_deleted(node)

        if (include_self or node is not root) and not node_deleted:
            yield node

        children = getattr(node, 'children', [])
        for child in children:
            queue.append((child, node_deleted))


def collect_nodes_by_internal_type(
        root,
        internal_types: Union[str, Iterable[str]]
) -> List:
    """Collect active descendants of ``root`` that match the provided types."""

    if isinstance(internal_types, str):
        types = {internal_types}
    else:
        types = set(internal_types)

    return [node for node in iter_project_nodes(root) if node.internal_type() in types]


def collect_active_descendants(root, include_self: bool = False) -> List:
    """Return all non-deleted descendants of ``root``.

    When ``include_self`` is ``True`` the ``root`` node itself is included in
    the resulting list (provided it is not marked as deleted).
    """

    return list(iter_project_nodes(root, include_self=include_self))
