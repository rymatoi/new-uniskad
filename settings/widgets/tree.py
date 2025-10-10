from PySide2.QtWidgets import QVBoxLayout

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from settings.models import SettingsNode
from settings.widgets.tabs import AppearanceTab

logger = app_logger.get_logger(__name__)


class SettingsTreeView(TreeView):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.DISABLE_MENU = True
        self.setHeaderHidden(True)
        self.link_nodes_with_tabs({
            SettingsNode: AppearanceTab
        })

    def _load_menu(self, mode='base_state', location='treeview'):
        return []

    def open_item(self, index):
        if not index.isValid():
            return

        if self.model() and self.model().rowCount(index) > 0:
            return

        if len(self._parent.ui.widget.children()):
            layout = self._parent.ui.widget.children()[0]
            tab = self._parent.ui.widget.children()[1]
            self._parent.ui.widget.clearLayout(layout)
            layout.deleteLater()
            tab.deleteLater()
        self._opened_tabs.clear()

        item = index.internalPointer()
        item_type = self.model().item_types.get(item.internal_type(), 'root')
        tab = self._link_dict.get(item_type, self._default_tab)(index, self, self.main_window)
        self._opened_tabs[index] = tab

        layout = QVBoxLayout(self.parent())
        layout.addWidget(tab)
        self._parent.ui.widget.setLayout(layout)
        tab.show()
