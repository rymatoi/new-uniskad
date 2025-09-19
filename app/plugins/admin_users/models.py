from PySide2.QtGui import QIcon

from app.basic_funcs import error
from app.plugins.admin_users.dialogs.create_user import CreateUserDialog
from app.plugins.base_state.models import Node, TreeModel
from db import sp, session
from db.schemas import User


class UserRootNode(Node):
    exclude_from_base_actions = ['_customize', '_rename_node']

    @staticmethod
    def internal_type():
        return 'root'

    @staticmethod
    def internal_actions():
        return ['add']

    @staticmethod
    def container_types():
        return [UserNode]


class ActiveFolder(Node):
    exclude_from_base_actions = ['_customize', '_rename_node', '_remove']

    @staticmethod
    def is_folder():
        return True

    @staticmethod
    def internal_type():
        return 'active_folder'

    @staticmethod
    def internal_actions():
        return []

    def data(self, column=0):
        return 'Активные'

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(":/folder.png")

    @staticmethod
    def container_types():
        return [UserNode]


class InactiveFolder(Node):
    exclude_from_base_actions = ['_customize', '_rename_node', '_remove']

    @staticmethod
    def is_folder():
        return True

    @staticmethod
    def internal_type():
        return 'inactive_folder'

    @staticmethod
    def internal_actions():
        return []

    def data(self, column=0):
        return 'Неактивные'

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(":/folder.png")

    @staticmethod
    def container_types():
        return [UserNode]


class UserNode(Node):
    exclude_from_base_actions = ['_customize', '_rename_node', '_remove']

    @staticmethod
    def internal_type():
        return 'user'

    @staticmethod
    def internal_actions():
        return []

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def data(self, column=0):
        return self._data.name + ' ' + self._data.fam

    def get_icon(self, column=0):
        if column == 0:
            return QIcon(":/user.png")

    @staticmethod
    def add(up_node_id, parent):
        dialog = CreateUserDialog()
        if dialog.exec_():
            data = dialog.get_result()
            result = sp.new_uniskaduser(*data)
            if result == -2 or (isinstance(result, User) and result.id is None):
                error('Ошибка создания пользователя', str(result))
            else:
                return UserNode(result)

    @staticmethod
    def remove(item, final=False):
        print('Попытка удалить пользователя', item._data.id)
        success = sp.del_restore_uniskaduser(item._data.id, True, final)
        print('Пользователь удален' if success else 'Пользователь не удален')
        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def restore(item):
        success = sp.del_restore_uniskaduser(item._data.id, False, False)
        if success:
            item._data.deleted = False
        return success


class AdminUsersTreeModel(TreeModel):

    def __init__(self):
        super().__init__()
        self._root = UserRootNode(None)
        self.register_nodes([UserNode, UserRootNode, ActiveFolder, InactiveFolder])
        self.inactive_folder = None
        self.active_folder = None

    # def _ini_tree(self, nodes, root, root_item, root_item_index=None):
    #     root_elements = [node for node in nodes if node.id_up == root and node.prop_name == self.display_prop]
    #     for element in root_elements:
    #         element_item = self.item_types.get(element.type_, self.item_types['root'])(element)
    #         self.insertRows(root_item.childCount(), [element_item],
    #                         root_item_index) if root_item_index else root_item.addChild(element_item)
    #         props = self._prop_dict.setdefault(element.id, [])
    #         for prop in props:
    #             if prop.prop_value:
    #                 setattr(element_item, prop.prop_name, prop.prop_value)
    #         child_items = [node for node in nodes if node.id_up == element.id]
    #         if any(child_items):
    #             self._ini_tree(nodes, element.id, element_item)
