"""Utility helpers for traversing project tree structures."""
from __future__ import annotations

from typing import Iterator, List, Optional, Sequence, Set, Union

NodeType = object


def _coerce_to_set(types: Union[str, Sequence[str]]) -> Set[str]:
    if isinstance(types, str):
        return {types}
    return set(types)


def _get_parent(node) -> Optional[NodeType]:
    parent_getter = getattr(node, "parent", None)
    if callable(parent_getter):
        return parent_getter()
    return None


def _get_children(node) -> List[NodeType]:
    children = getattr(node, "children", None)
    if children is None:
        return []
    return list(children)


def is_node_deleted(node) -> bool:
    """Return True if the node or its data is marked as deleted."""
    data = getattr(node, "_data", None)
    if data is None:
        return False
    deleted = getattr(data, "deleted", False)
    if isinstance(deleted, str):
        return deleted.lower() == "true"
    return bool(deleted)


def get_tree_root(node) -> Optional[NodeType]:
    """Return the top-most ancestor for the given node."""
    current = node
    while current is not None:
        parent = _get_parent(current)
        if parent is None:
            break
        current = parent
    return current


def iter_tree_nodes(
    root,
    *,
    include_deleted: bool = False,
    skip_root: bool = False,
):
    """Iterate over nodes in the tree starting from *root*.

    Args:
        root: Starting node of the traversal.
        include_deleted: When ``False`` (default) nodes marked as deleted or
            located under deleted ancestors are skipped.
        skip_root: When ``True`` the *root* node itself is not yielded.
    """
    if root is None:
        return

    stack = [(root, False)]
    while stack:
        node, ancestor_deleted = stack.pop()
        node_deleted = is_node_deleted(node)
        path_deleted = ancestor_deleted or node_deleted

        if not (skip_root and node is root):
            if include_deleted or not path_deleted:
                yield node

        children = _get_children(node)
        if children:
            for child in reversed(children):
                stack.append((child, path_deleted))


def find_nodes_by_type(
    root,
    types: Union[str, Sequence[str]],
    *,
    include_deleted: bool = False,
    skip_root: bool = False,
) -> List[NodeType]:
    """Return a list of nodes matching the requested *types*.

    Args:
        root: Starting node for the search.
        types: Single type or sequence of types to look for (matches the value
            returned by ``internal_type()``).
        include_deleted: When ``True`` nodes under deleted ancestors are
            returned as well.
        skip_root: When ``True`` the *root* node itself is not considered even
            if its type matches.
    """
    type_set = _coerce_to_set(types)
    result: List[NodeType] = []
    for node in iter_tree_nodes(root, include_deleted=include_deleted, skip_root=skip_root):
        internal_type = getattr(node, "internal_type", None)
        if internal_type is None:
            continue
        try:
            node_type = internal_type()
        except TypeError:
            # ``internal_type`` might be defined without ``self``.
            node_type = internal_type  # type: ignore[assignment]
        if node_type in type_set:
            result.append(node)
    return result


def find_first_ancestor_by_type(
    node,
    types: Union[str, Sequence[str]],
) -> Optional[NodeType]:
    """Find the first ancestor matching any of *types*.

    Args:
        node: Node to start from (itself is not considered).
        types: Type or types to match against ``internal_type()``.
    """
    type_set = _coerce_to_set(types)
    current = _get_parent(node)
    while current is not None:
        internal_type = getattr(current, "internal_type", None)
        if internal_type is not None:
            try:
                current_type = internal_type()
            except TypeError:
                current_type = internal_type  # type: ignore[assignment]
            if current_type in type_set:
                return current
        current = _get_parent(current)
    return None
