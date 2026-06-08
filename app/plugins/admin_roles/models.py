from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from app.basic_funcs import info, error
from app.plugins.admin_roles.dialogs.create_role import CreateRoleDialog
from app.plugins.base_state.models import Node, TreeModel
from config.config import PROG_ID
from db import sp


class RoleRootNode(Node):
    exclude_from_base_actions = ['_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'root'

    @staticmethod
    def container_types():
        return [RoleNode]

    @staticmethod
    def internal_actions():
        return ['add']

    def data(self, column=0):
        return self._data.rolename

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(":/role.png")


class RoleNode(RoleRootNode):
    exclude_from_base_actions = ['_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'role'

    @staticmethod
    def container_types():
        return [RoleNode]

    @staticmethod
    def internal_actions():
        return ['add']

    @staticmethod
    def self_internal_actions():
        return ['remove']

    @staticmethod
    def add(up_node_id, parent):
        dialog = CreateRoleDialog()
        if dialog.exec_():
            rolename, description = dialog.get_result()
            result = sp.new_upd_uniskadrole((PROG_ID, None, up_node_id, rolename, description, False, False))
            if result:
                return RoleNode(result)
            else:
                error('Ошибка создания роли', 'Ошибка создания роли.')

    @staticmethod
    def remove(item, final=False):
        success = sp.del_restore_uniskadrole(item._data.id, True, final)
        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def restore(item):
        success = sp.del_restore_uniskadrole(item._data.id, False, False)
        if success:
            item._data.deleted = False
        return success


class ActionNode(Node):

    @staticmethod
    def internal_type():
        return 'action'

    def check(self, state):
        self.checked = state
        sp.grant_remove_role_menu_link(self._data.id_role, self._data.id, True if state else False)

    def is_checked(self):
        return self.checked

    def data(self, column=0):
        return self._data.translation

    @staticmethod
    def container_types():
        return [ActionNode]

    def get_icon(self, column=0):
        return QIcon()


class ModeNode(Node):

    @staticmethod
    def internal_type():
        return 'mode'

    def check(self, state):
        self.checked = state

    def is_checked(self):
        if len(self.checked_children_count()) == 0:
            return Qt.Unchecked
        if len(self.checked_children_count()) == self.childCount():
            return Qt.Checked
        else:
            return Qt.PartiallyChecked

    def data(self, column=0):
        return self._data.rejim_name_rus

    @staticmethod
    def container_types():
        return [ActionNode, LocationNode]


class LocationNode(Node):

    @staticmethod
    def internal_type():
        return 'location'

    def check(self, state):
        self.checked = state

    def is_checked(self):
        if len(self.checked_children_count()) == 0:
            return Qt.Unchecked
        if len(self.checked_children_count()) == self.childCount():
            return Qt.Checked
        else:
            return Qt.PartiallyChecked

    def data(self, column=0):
        return self._data.translation

    @staticmethod
    def container_types():
        return [ActionNode]


class AdminRolesTreeModel(TreeModel):

    def __init__(self):
        super().__init__()
        self._root = RoleRootNode(None)  # переопределяем корень
        self.register_nodes([RoleRootNode, RoleNode])


class RoleActionTreeModel(TreeModel):
    CHECKABLE = True

    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)
        self.register_nodes([ActionNode, ModeNode, LocationNode])
