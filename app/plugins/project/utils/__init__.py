from typing import Iterable, Iterator, List, Optional, Sequence, Set, Union

from .utils_ import collect_project_params

NodeLike = Union["TreeNodeProtocol", Sequence["TreeNodeProtocol"], None]


class TreeNodeProtocol:
    """Protocol-like minimal interface for project tree nodes."""

    def internal_type(self) -> str:  # pragma: no cover - runtime protocol
        ...

    @property
    def children(self) -> Sequence["TreeNodeProtocol"]:  # pragma: no cover - runtime protocol
        ...

    @property
    def _data(self):  # pragma: no cover - runtime protocol
        ...


def _iter_nodes(root: NodeLike) -> Iterator["TreeNodeProtocol"]:
    """Iterate over the tree starting from *root* preserving child order."""

    if root is None:
        return

    if isinstance(root, (list, tuple, set)):
        stack: List["TreeNodeProtocol"] = [node for node in reversed(list(root)) if node is not None]
    else:
        stack = [root] if root is not None else []

    while stack:
        node = stack.pop()
        if node is None:
            continue
        yield node
        children = getattr(node, "children", None)
        if children:
            for child in reversed(children):
                stack.append(child)


def find_nodes_by_type(root: NodeLike, types: Union[str, Iterable[str]]) -> List["TreeNodeProtocol"]:
    """Return all nodes with ``internal_type`` contained in *types* starting from *root*."""

    if isinstance(types, str):
        type_set: Set[str] = {types}
    else:
        type_set = set(types)
    return [node for node in _iter_nodes(root) if getattr(node, "internal_type", lambda: None)() in type_set]


def find_first_node_by_type(root: NodeLike, types: Union[str, Iterable[str]]) -> Optional["TreeNodeProtocol"]:
    """Return the first node matching ``internal_type`` from *types* starting from *root*."""

    if isinstance(types, str):
        type_set: Set[str] = {types}
    else:
        type_set = set(types)
    for node in _iter_nodes(root):
        if getattr(node, "internal_type", lambda: None)() in type_set:
            return node
    return None


def is_node_deleted(node) -> bool:
    """Normalise the ``deleted`` flag for tree nodes."""

    data = getattr(node, "_data", None)
    deleted = getattr(data, "deleted", False)
    if isinstance(deleted, str):
        return deleted.lower() == "true"
    return bool(deleted)


__all__ = [
    "collect_project_params",
    "find_nodes_by_type",
    "find_first_node_by_type",
    "is_node_deleted",
]
