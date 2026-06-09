from PySide6.QtCore import Qt, QModelIndex

from app import app_logger
from app.plugins.admin_users.models import UserNode, ActiveFolder, InactiveFolder
from app.plugins.admin_users.widgets.tabs import UserTab
from app.plugins.base_state.widgets import TreeView
from db.schemas import User

logger = app_logger.get_logger(__name__)


class AdminUsersTreeView(TreeView):
    SHOW_ONLY_BLOCKED = False
    SHOW_ACTIVENESS = False

    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('admin_users', 'users_treeview')
        self.link_nodes_with_tabs({
            UserNode: UserTab,
        })

        self.active_folder = None
        self.inactive_folder = None

    # def refresh(self):
    #     for row in range(self.model().rowCount()):
    #         index = self.model().index(row, 0)
    #         if not index.internalPointer():
    #             continue
    #         hidden = self.model().data(index, Qt.ItemDataRole.UserRole)
    #         if not self.HIDE_REMOVED_ITEMS:
    #             self.setItemVisibility(self.model(), index, False)
    #         else:
    #             self.setItemVisibility(self.model(), index, hidden)
        # self.dataChanged(index, index)

    def add_folders(self, add_flag):
        if add_flag:
            active_folder = ActiveFolder(User({'id': -10, 'id_up': 0, 'type_': 'active_folder', 'deleted': False}))
            inactive_folder = InactiveFolder(
                User({'id': -10, 'id_up': 0, 'type_': 'inactive_folder', 'deleted': False}))
            self.model().addChild(active_folder, QModelIndex())
            self.model().addChild(inactive_folder, QModelIndex())
            self.active_folder = active_folder
            self.inactive_folder = inactive_folder
        else:
            self.model().removeChild(self.active_folder.row(), QModelIndex())
            self.model().removeChild(self.inactive_folder.row(), QModelIndex())

    def sort_items_to_folders(self, sort_flag):
        active_items = []
        inactive_items = []
        all_items = []
        if sort_flag:
            for row in range(self.model().rowCount()):
                index = self.model().index(row, 0)
                item = index.internalPointer()
                if not item or item.internal_type() in ['active_folder', 'inactive_folder']:
                    continue
                if item._data.active:
                    active_items.append(item)
                else:
                    inactive_items.append(item)

            for item in active_items:
                if item.parent():
                    item.parent().removeChild(item.row())
                self.model().addChild(item, self.model().index(self.active_folder.row(), 0))

            for item in inactive_items:
                if item.parent():
                    item.parent().removeChild(item.row())
                self.model().addChild(item, self.model().index(self.inactive_folder.row(), 0))
        else:
            for item in self.active_folder._children + self.inactive_folder._children:
                item.parent().removeChild(item.row())
                self.model().addChild(item, QModelIndex())
