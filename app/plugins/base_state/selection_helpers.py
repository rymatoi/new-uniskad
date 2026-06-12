"""Small, local helpers shared by checkable selection dialogs."""

from time import perf_counter

from PySide2.QtCore import QModelIndex, Qt

from app import app_logger


logger = app_logger.get_logger(__name__)


def iter_model_indexes(model, parent=QModelIndex()):
    """Yield every currently exposed index in model order."""
    for row in range(model.rowCount(parent)):
        index = model.index(row, 0, parent)
        if not index.isValid():
            continue
        yield index
        yield from iter_model_indexes(model, index)


def visible_source_indexes(proxy):
    """Return enabled/checkable source indexes accepted by the current filter."""
    indexes = []
    seen = set()
    source_model = proxy.sourceModel()
    for proxy_index in iter_model_indexes(proxy):
        source_index = proxy.mapToSource(proxy_index)
        node = source_index.internalPointer()
        if node is None or id(node) in seen:
            continue
        flags = source_model.flags(source_index)
        if not flags & Qt.ItemIsEnabled or not flags & Qt.ItemIsUserCheckable:
            continue
        seen.add(id(node))
        indexes.append(source_index)
    return indexes


def set_visible_checked(dialog, state, action):
    """Set check state for the filtered rows using one model reset/repaint."""
    started = perf_counter()
    model = dialog.model
    view = dialog.ui.treeView
    indexes = visible_source_indexes(dialog.proxy)
    nodes = [index.internalPointer() for index in indexes]
    affected_nodes = set(nodes)

    view.setUpdatesEnabled(False)
    try:
        model.beginResetModel()
        try:
            if state == Qt.Checked:
                checked_nodes = set(model.checked_list)
                model.checked_list.extend(node for node in nodes if node not in checked_nodes)
            else:
                model.checked_list = [node for node in model.checked_list if node not in affected_nodes]
            for node in nodes:
                node.check(state)
        finally:
            model.endResetModel()
    finally:
        view.setUpdatesEnabled(True)
        view.viewport().update()

    if hasattr(dialog, 'selection_batch_completed'):
        dialog.selection_batch_completed()
    elif hasattr(dialog, 'change_selected'):
        dialog.change_selected(None)
    logger.info(
        "SelectionDialog %s completed: class=%s, affected=%d, selected=%d, elapsed=%.4fs",
        action, dialog.__class__.__name__, len(nodes), len(model.checked_list), perf_counter() - started,
    )


def apply_filter(dialog, text):
    """Apply an existing proxy filter and log its cost without changing semantics."""
    started = perf_counter()
    view = dialog.ui.treeView
    view.setUpdatesEnabled(False)
    try:
        dialog.proxy.setFilterRegExp(dialog._selection_filter(text))
    finally:
        view.setUpdatesEnabled(True)
        view.viewport().update()
    visible = sum(1 for _index in iter_model_indexes(dialog.proxy))
    total = sum(1 for _index in iter_model_indexes(dialog.model))
    logger.info(
        "SelectionDialog filter completed: class=%s, visible=%d, total=%d, elapsed=%.4fs",
        dialog.__class__.__name__, visible, total, perf_counter() - started,
    )


def log_initialized(dialog, items, started):
    logger.info(
        "SelectionDialog initialized: class=%s, items=%d, elapsed=%.4fs",
        dialog.__class__.__name__, items, perf_counter() - started,
    )
