from PySide2.QtWidgets import QAbstractItemView, QVBoxLayout

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from settings.models import SettingsNode
from settings.widgets.tabs import AppearanceTab

logger = app_logger.get_logger(__name__)


class SettingsTreeView(TreeView):
    def __init__(self, parent, main_window):
        self.DISABLE_MENU = True
        super().__init__(parent, main_window)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(False)

        self.link_nodes_with_tabs({
            SettingsNode: AppearanceTab
        })

    def _load_menu(self, *args, **kwargs):  # type: ignore[override]
        return []

    def setModel(self, model):  # type: ignore[override]
        super().setModel(model)
        selection_model = self.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(lambda current, _: self.open_item(current))

    def open_item(self, index):
        if not index or not index.isValid():
            return

        item = index.internalPointer()
        if item is None:
            return

        container = self._parent.ui.widget
        existing_layout = container.layout()
        if existing_layout is not None:
            while existing_layout.count():
                child_item = existing_layout.takeAt(0)
                widget = child_item.widget()
                if widget is not None:
                    widget.deleteLater()
            existing_layout.deleteLater()

        tab_class = getattr(item, 'tab_class', None)
        if tab_class is None:
            item_type = self.model().item_types.get(item.internal_type(), 'root')
            tab_class = self._link_dict.get(item_type, self._default_tab)

        tab = tab_class(index, self, self.main_window)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tab)
        container.setLayout(layout)
        tab.show()
        self._opened_tabs.clear()
        self._opened_tabs[index] = tab
