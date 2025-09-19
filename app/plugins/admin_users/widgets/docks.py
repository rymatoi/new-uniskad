from app.plugins.base_state.widgets import DockWidget


class AdminUsersDockWidget(DockWidget):

    def init_menu(self):
        super().init_menu()
        self.settings_menu += self._load_menu('admin_users', 'admin_users_settings_tool_button')
        self.init_settings()

    def connect_triggered_funcs(self, index=None):
        super().connect_triggered_funcs(index)

        self._connect_func('_activeness', lambda: self.change_view('activeness'))
        self._connect_func('_blocked', lambda: self.change_view('blocked'))

    def init_settings(self):
        for action in ['_activeness', '_blocked', '_show_removed']:
            if hasattr(self, action) and getattr(self, action).isChecked():
                self.change_view(action[1:])

    def change_view(self, view):
        if view == 'activeness':
            if self.tree_widget:
                self.tree_widget.add_folders(getattr(self, '_activeness').isChecked())
                self.tree_widget.sort_items_to_folders(getattr(self, '_activeness').isChecked())
                self.tree_widget.refresh()
        elif view == 'blocked':
            pass
