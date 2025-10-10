from PySide2 import QtCore
from PySide2.QtWidgets import QVBoxLayout

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from settings.models import SettingsNode
from settings.widgets.tabs import AppearanceTab, GeneralTab

logger = app_logger.get_logger(__name__)


class SettingsTreeView(TreeView):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.DOUBLE_CLICK_OPEN = False
        self._default_tab = AppearanceTab
        self.link_nodes_with_tabs({
            SettingsNode: AppearanceTab,
            'appearance': AppearanceTab,
            'general': GeneralTab
        })

    def open_item(self, index):
        if not index or not index.isValid():
            return

        item = index.internalPointer()
        if item is None:
            return

        tab_cls = self._tab_for_item(item)
        container = self._parent.ui.widget
        layout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
            container.setLayout(layout)
        else:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()

        tab = tab_cls(index, self, self.main_window)
        layout.addWidget(tab)
        tab.show()

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:  # type: ignore[override]
        super().setModel(model)
        selection_model = self.selectionModel()
        if selection_model is not None:
            selection_model.currentChanged.connect(self._on_current_changed)

    def _on_current_changed(self, current, _previous):
        if current and current.isValid():
            self.open_item(current)

    def _tab_for_item(self, item):
        tab_id = getattr(item, 'tab_id', None)
        if tab_id:
            tab_cls = self._link_dict.get(tab_id)
            if tab_cls is not None:
                return tab_cls
        item_type = self.model().item_types.get(item.internal_type(), 'root')
        return self._link_dict.get(item_type, self._default_tab)
