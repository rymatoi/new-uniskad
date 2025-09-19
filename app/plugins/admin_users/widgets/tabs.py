from PySide2.QtCore import QModelIndex

from app.basic_funcs import error
from app.plugins.admin_roles.models import AdminRolesTreeModel
from app.plugins.admin_roles.widgets import AdminRolesTreeView
from app.plugins.admin_users.dialogs.link_role import LinkRoleDialog
from app.plugins.base_state.widgets import Tab
from config import config
from db import sp
from resources.ui.ui_py.ui_edit_user import Ui_EditUser


class UserTab(Tab):
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self.setupUi(Ui_EditUser())

        self.user_roles = None

        self.init_treeview()
        self.init_values()
        self.create_connections()

    def init_treeview(self):
        roles_model = AdminRolesTreeModel()
        self.user_roles = sp.get_user_role_list_by_id(self.item._data.id)
        roles_model.ini_tree(self.user_roles)

        self.ui.treeView_ = AdminRolesTreeView(self, self.main_window)
        self.ui.treeView_.DOUBLE_CLICK_OPEN = False
        self.ui.treeView_.DISABLE_MENU = True
        self.ui.treeView_.setModel(roles_model)

        self.ui.gridLayout.replaceWidget(self.ui.treeView, self.ui.treeView_)
        self.ui.treeView.deleteLater()

    def init_values(self):
        # timeout = self.main_window.user_settings.get('application_close_timeout')
        # if timeout:
        #     self.ui.spinBox_2.setValue(int(timeout))
        # else:
        #     self.ui.spinBox_2.setValue(
        #         int(sp.get_default_value(None, None, 'uniskadusers', 'application_close_timeout')['get_default_value']))

        user_settings = sp.get_user_default_value(None, self.item._data.login, None, 'application_close_timeout')

        if user_settings['get_user_default_value']:
            self.ui.spinBox_2.setValue(int(user_settings['get_user_default_value']))
        else:
            self.ui.spinBox_2.setValue(
                int(sp.get_default_value(None, None, 'uniskadusers', 'application_close_timeout')['get_default_value']))

        self.ui.usernameLineEdit_2.setText(self.item._data.login)
        self.ui.nameLineEdit.setText(self.item._data.name)
        self.ui.surnameLineEdit.setText(self.item._data.fam)
        self.ui.activeCheckBox.setChecked(self.item._data.active)
        self.ui.lastLoginLineEdit.setText(self.item._data.last_login)
        self.ui.lastLogoutLineEdit.setText(self.item._data.last_logout)
        self.ui.spinBox.setValue(self.item._data.default_password_fail_count)
        self.ui.leftSpinBox.setValue(self.item._data.password_fail_count)
        self.ui.deletedCheckBox.setChecked(self.item._data.deleted)

    def create_connections(self):
        self.ui.buttonBox_2.accepted.connect(self.save_values)
        self.ui.removeButton.clicked.connect(self.remove_roles)
        self.ui.buttonBox_2.rejected.connect(self.close)
        self.ui.addButton.clicked.connect(self.link_new_role)

    def remove_roles(self):
        selected_index = self.ui.treeView_.selectedIndexes()
        if selected_index:
            index = selected_index[0]
            item = index.internalPointer()
            success = sp.unlink_user_role_array(self.item._data.id, [item._data.id])
            if success:
                self.ui.treeView_.removeRow(index.row(), index.parent())
            else:
                error('Ошибка!', "Не удалось удалить отношение.")

    def link_new_role(self):
        dialog = LinkRoleDialog(self.item, exclude=[item.rolename for item in self.user_roles])
        if dialog.exec_():  # Если произошло изменение данных
            if res := dialog.get_result():
                self.ui.treeView_.insertRows(res, QModelIndex())

    def save_values(self):
        self.item._data.login = self.ui.usernameLineEdit_2.text()
        self.item._data.name = self.ui.nameLineEdit.text()
        self.item._data.fam = self.ui.surnameLineEdit.text()
        self.item._data.active = self.ui.activeCheckBox.isChecked()
        self.item._data.last_login = self.ui.lastLoginLineEdit.text()
        self.item._data.last_logout = self.ui.lastLogoutLineEdit.text()
        self.item._data.default_password_fail_count = self.ui.spinBox.value()
        self.item._data.password_fail_count = self.ui.leftSpinBox.value()
        self.item._data.deleted = self.ui.deletedCheckBox.isChecked()

        sp.update_uniskaduser(
            p_user_id=self.item._data.id,
            p_new_user_id_prog=config.PROG_ID,
            p_new_user_login=self.item._data.login,
            p_new_user_fam=self.item._data.fam,
            p_new_user_name=self.item._data.name,
            p_new_user_id_role=self.item._data.default_id_role,
            p_new_user_active=self.item._data.active,
            p_new_user_deleted=self.item._data.deleted,
            p_new_user_password_fail_count=self.item._data.password_fail_count,
            p_new_user_default_password_fail_count=self.item._data.default_password_fail_count
        )

        a = sp.set_user_default_value(None, self.item._data.login, None, 'application_close_timeout',
                                      str(self.ui.spinBox_2.value()))
        self.main_window.user_settings.update()
        self.refresh(self.index)
