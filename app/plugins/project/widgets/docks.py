from app.plugins.base_state.widgets import DockWidget
from db import sp


class ProjectDockWidget(DockWidget):

    def __init__(self, title, menu_name, plugin_name, parent=None):
        super().__init__(title, menu_name, plugin_name, parent)
        self.project_id = None

    def init_project_id(self, project):
        self.project_id = project.id

    def save_state(self):
        if not self.tree_widget:
            return
        update_data = self.update_npps(self.tree_widget.model()._root)
        sp.new_update_project_from_record_array(update_data)
