from copy import copy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QCheckBox

from app import app_logger
from app.plugins.admin_roles.models import RoleActionTreeModel, RoleNode
from app.plugins.base_state.widgets import TreeView, Tab
from db import sp

logger = app_logger.get_logger(__name__)


class AdminRoleTab(Tab):
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        model = RoleActionTreeModel()
        tree_items = self.make_tree()
        model.ini_tree(tree_items)

        widget = QWidget()
        vl = QVBoxLayout()
        widget.setLayout(vl)

        form_l = QFormLayout()
        self.limited_access_chbx = QCheckBox('')
        self.limited_access_chbx.setChecked(self.item._data.access_secret_data)
        form_l.addRow('Доступ к параметрам ограниченной видимости:', self.limited_access_chbx)

        self.treeview = TreeView(self)
        self.treeview.setModel(model)

        vl.addLayout(form_l)
        vl.addWidget(self.treeview)

        self.setWidget(widget)

    def make_tree(self):
        actions = sp.get_all_menus()
        checked_actions = sp.get_all_user_menu_(self.item._data.id_role)
        modes = sp.get_modes()
        locations = sp.get_locations()

        used_mode_locations = {(action.mode, action.location) for
                               action in actions}

        for mode in modes:
            mode.id = mode.rejim_name_base

        _locations = []
        for mode, location in used_mode_locations:
            _mode = self.get_mode_by_name(mode, modes)
            _loc = self.get_location_by_name(location, locations)
            _loc.mode = mode
            _loc.id_up = _mode.rejim_name_base
            _locations.append(_loc)

        for action in actions:
            if action.is_root:
                action.id_up = [_loc for _loc in _locations if
                                _loc.name == action.location and _loc.mode == action.mode][0].id
            action.id_role = self.item._data.id_role

        for action in checked_actions:
            action.prop_name = 'checked'
            action.prop_value = Qt.CheckState.Checked

        return modes + _locations + actions + checked_actions

    def get_mode_by_name(self, name, modes):
        if name == 'any':
            name = 'base_state'
        return [mode for mode in modes if mode.rejim_name_base == name][0]

    def get_location_by_name(self, name, locations):
        return copy([location for location in locations if location.name == name][0])

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        sp.grant_role_secret_access(self.item._data.id_role, self.limited_access_chbx.isChecked())
        self.item._data.access_secret_data = self.limited_access_chbx.isChecked()


class AdminRolesTreeView(TreeView):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('admin_roles', 'roles_treeview')
        self.link_nodes_with_tabs({
            RoleNode: AdminRoleTab
        })
