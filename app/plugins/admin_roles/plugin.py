from app import app_logger
from app.plugins.admin_roles.models import AdminRolesTreeModel
from app.plugins.admin_roles.widgets import AdminRolesTreeView
from app.plugins.base_state.plugin import BasePlugin
from db import sp

logger = app_logger.get_logger(__name__)


class AdminRolesPlugin(BasePlugin):
    def __init__(self, parent):
        super().__init__(parent)
        self.roles_treeview = None

    def activate(self):
        logger.info("Активирован подрежим Администрирование ролей.")

        model = AdminRolesTreeModel()
        roles = sp.get_roles()
        model.ini_tree(roles)

        self.roles_treeview = AdminRolesTreeView(self._parent, main_window=self._parent)
        self.roles_treeview.setModel(model)
        return True

    def tree_view(self):
        return self.roles_treeview

    def deactivate(self):
        logger.info("Деактивирован режим Администрирование ролей.")
        return super(AdminRolesPlugin, self).deactivate()
