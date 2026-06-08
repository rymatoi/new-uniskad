from app import app_logger
from app.plugins.base_state.plugin import BasePlugin
from app.plugins.project.dialogs.select_project import ProjectSelectionDialog
from app.plugins.project.models import ProjectTreeModel, ProjectRoot
from app.plugins.project.widgets.tree import ProjectTreeView
from db import sp

logger = app_logger.get_logger(__name__)


class ProjectPlugin(BasePlugin):

    def __init__(self, parent):
        super().__init__(parent)
        self.project_treeview = None
        self.autoopen_project_id = None

    def tree_view(self):
        return self.project_treeview

    def activate(self):
        dialog = ProjectSelectionDialog(self.autoopen_project_id, main_window=self.parent())
        if dialog.exec():
            project = dialog.get_result()

            # self.project_treeview = TreeWidget(dialog.projects, project.project_id)

            model = ProjectTreeModel()
            model.root_id = project.project_id
            model._root = ProjectRoot(project)
            model.ini_tree(dialog.projects)
            self.project_treeview = ProjectTreeView(self._parent, main_window=self.main_window)
            self.project_treeview.setModel(model)
            self.dock_widget_name = project.project_prop_value
            self.main_window.project_tree_dock_widget.init_project_id(dialog.get_result())
            logger.info("Активирован режим Проект.")
            self.autoopen_project_id = None
            return True
