from typing import Dict, Type

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QWidget

from app import app_logger
from app.plugins.base_state.widgets import TreeView
from settings.models import SettingsNode
from settings.widgets.tabs import AppearanceTab
from settings.widgets.general import GeneralTab

logger = app_logger.get_logger(__name__)


class SettingsTreeView(TreeView):
    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.tab_registry: Dict[str, Type[QWidget]] = {
            'appearance': AppearanceTab,
            'general': GeneralTab,
        }
        self.link_nodes_with_tabs({
            SettingsNode: AppearanceTab
        })

    def open_item(self, index: QModelIndex):
        if not index or not index.isValid():
            return

        item = index.internalPointer()
        if item is None:
            return

        tab_key = getattr(item, 'tab', None)
        tab_class = None
        if isinstance(tab_key, str):
            tab_class = self.tab_registry.get(tab_key.lower())

        if tab_class is None:
            item_type = self.model().item_types.get(item.internal_type(), 'root')
            tab_class = self._link_dict.get(item_type, self._default_tab)

        if tab_class is None:
            logger.warning('Для узла %s не найден класс вкладки', getattr(item, 'name', item))
            return

        tab = tab_class(index, self, self.main_window)
        if hasattr(self._parent, 'display_settings_tab'):
            self._parent.display_settings_tab(tab)
        else:
            tab.show()
