from app.plugins.base_state.widgets import DockWidget
from db import sp


class ProjectDockWidget(DockWidget):

    def __init__(self, title, menu_name, plugin_name, parent=None):
        super().__init__(title, menu_name, plugin_name, parent)
        self.project_id = None

    def init_project_id(self, project):
        self.project_id = project.id
        parent = getattr(self, '_parent', None)
        if parent and hasattr(parent, 'user_settings'):
            try:
                setting = parent._ui_state_setting('active_project') \
                    if hasattr(parent, '_ui_state_setting') else 'active_project'
                parent.user_settings.set(setting, str(project.id))
            except Exception:
                pass

    def save_state(self):
        tree = self.widget()
        if not tree or not hasattr(tree, 'model'):
            return
        if hasattr(tree, 'has_pending_save') and not tree.has_pending_save():
            return
        model = tree.model()
        if model is None:
            return
        update_data = self.update_npps(model._root)
        if not update_data:
            if hasattr(tree, 'clear_pending_save'):
                tree.clear_pending_save()
            return
        sp.new_update_project_from_record_array(update_data)
        if hasattr(tree, 'clear_pending_save'):
            tree.clear_pending_save()
