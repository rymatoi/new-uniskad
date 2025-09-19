from PySide2.QtWidgets import QTreeView

from app import app_logger
from app.plugins.admin_users.models import AdminUsersTreeModel
from app.plugins.admin_users.widgets.tree import AdminUsersTreeView
from app.plugins.base_state.plugin import BasePlugin
from db import sp
from db.schemas import User

logger = app_logger.get_logger(__name__)


class AdminUsersPlugin(BasePlugin):
    def __init__(self, parent):
        super().__init__(parent)
        self.users_treeview = None

    def activate(self):
        logger.info("Активирован подрежим Администрирование пользователей.")

        model = AdminUsersTreeModel()
        users = sp.get_full_users_list()

        # activeFolder = User({'id': -10, 'id_up': 0, 'type_': 'active_folder', 'deleted': False})
        # inactiveFolder = User({'id': -20, 'id_up': 0, 'type_': 'inactive_folder', 'deleted': False})

        model.ini_tree(users)

        self.users_treeview = AdminUsersTreeView(self._parent, main_window=self._parent)
        self.users_treeview.setModel(model)
        self.users_treeview.setSelectionMode(QTreeView.SingleSelection)

        # self.users_treeview.add_folders(True)
        # self.users_treeview.sort_items_to_folders(True)
        # self.users_treeview.refresh()

        # self.users_treeview.add_folders(False)
        # self.users_treeview.sort_items_to_folders(False)
        # self.users_treeview.refresh()

        return True

    def tree_view(self):
        return self.users_treeview

    def deactivate(self):
        logger.info("Деактивирован режим Администрирование.")
        return super(AdminUsersPlugin, self).deactivate()
