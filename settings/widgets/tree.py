from PySide2.QtWidgets import QAbstractItemView, QTreeView, QVBoxLayout

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from settings.models import SettingsNode
from settings.widgets.tabs import AppearanceTab, GeneralTab

logger = app_logger.get_logger(__name__)


class SettingsTreeView(TreeView):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.setHeaderHidden(True)
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.DISABLE_MENU = True
        self._tab_factories = {
            'appearance': AppearanceTab,
            'general': GeneralTab,
        }
        self.link_nodes_with_tabs({
            SettingsNode: AppearanceTab
        })

    def _load_menu(self, mode='base_state', location='treeview'):
        return []

    def set_tab_factories(self, factories):
        self._tab_factories.update(factories)

    def setModel(self, model):
        super().setModel(model)
        self.expandAll()
        first_index = model.index(0, 0)
        if first_index.isValid():
            self.setCurrentIndex(first_index)
            self.open_item(first_index)

    def open_item(self, index):
        if self._opened_tabs.get(index, None):
            return

        if len(self._parent.ui.widget.children()):
            layout = self._parent.ui.widget.children()[0]
            tab = self._parent.ui.widget.children()[1]
            self._parent.ui.widget.clearLayout(layout)
            layout.deleteLater()
            tab.deleteLater()

        item = index.internalPointer()
        tab_key = getattr(item, 'tab', None)
        tab_factory = None
        if tab_key:
            tab_factory = self._tab_factories.get(tab_key)
        if tab_factory is None:
            item_type = self.model().item_types.get(item.internal_type(), 'root')
            tab_factory = self._link_dict.get(item_type, self._default_tab)
        tab = tab_factory(index, self, self.main_window)
        self._opened_tabs[index] = tab

        layout = QVBoxLayout(self.parent())
        layout.addWidget(tab)
        self._parent.ui.widget.setLayout(layout)
        tab.show()
