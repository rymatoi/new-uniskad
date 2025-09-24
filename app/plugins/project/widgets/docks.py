from app.plugins.base_state.widgets import DockWidget
from db import sp


class ProjectDockWidget(DockWidget):

    def __init__(self, title, menu_name, plugin_name, parent=None):
        super().__init__(title, menu_name, plugin_name, parent)
        self.project_id = None

    def init_project_id(self, project):
        self.project_id = project.id

    def save_state(self):
        tree = self.widget()
        if not tree or not hasattr(tree, 'model'):
            return
        model = tree.model()
        if model is None:
            return
        update_data = self.update_npps(model._root)
        if not update_data:
            return
        sp.new_update_project_from_record_array(update_data)
