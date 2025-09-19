import json
from app import app_logger, basic_funcs
from app.plugins.base_state.widgets import TreeView
from app.plugins.project.dialogs.edit_plot_templates import EditPlotTemplatesDialog
from app.plugins.project.dialogs.select_project import ProjectSelectionDialog
from app.plugins.project.dialogs.select_project_test import ProjectTestSelectionDialog
from app.plugins.project.models import GraphNode, TestNode, EpureNode, ProductFolderNode, FileNode
from app.plugins.project.widgets.tabs import TestTableTab, GraphTab, FileTab
from db import sp

logger = app_logger.get_logger(__name__)


class ProjectTreeView(TreeView):

    def __init__(self, parent, main_window):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('project', 'project_treeview')
        self.link_nodes_with_tabs({
            TestNode: TestTableTab,
            GraphNode: GraphTab,
            EpureNode: GraphTab,
            FileNode: FileTab
        })

    def connect_triggered_funcs(self, index):
        super().connect_triggered_funcs(index)

        self._connect_func('_import_test', self.import_test, index)
        self._connect_func('_save_graph_template', self.save_graph_template, index)
        self._connect_func('_apply_graph_template', self.apply_graph_template, index)

    def add_item(self, type_, index):
        super().add_item(type_, index)
        self.model().update_external_graphs()

    def remove(self, index, final=False):
        super().remove(index, final)
        self.model().update_external_graphs()

    def restore(self, index):
        super().restore(index)
        self.model().update_external_graphs()

    def import_test(self, index):
        dialog = ProjectSelectionDialog(main_window=self.main_window)
        item = index.internalPointer()
        if dialog.exec_():
            project = dialog.get_result()
            product_folder = None
            for child in project.children:
                if isinstance(child, ProductFolderNode):
                    product_folder = child
            if product_folder:
                test_select_dialog = ProjectTestSelectionDialog(product_folder._data.project_id,
                                                                main_window=self.main_window)
                if test_select_dialog.exec_():
                    selected = test_select_dialog.get_result()
                    current_item = selected[0]
                    while current_item.parent() in selected:
                        current_item = current_item.parent()
                    parent_id = current_item._data.project_id_up
                    up_node_id = item._data.project_id
                    data_objects = []
                    for obj in selected:
                        data_objects += [_obj.table_fit(item.scheme) for _obj in obj.obj_list]
                    result = sp.copy_tree_project_bunch(list(set(data_objects)), parent_id,
                                                        up_node_id)

    def save_graph_template(self, index):
        folder = index.internalPointer()
        name = basic_funcs.get_text('Имя шаблона', 'Введите имя шаблона', 'Шаблон')

        value = {
            'name': name,
            'axis': []
        }
        for child in folder.children:
            if hasattr(child._data, 'deleted') and child._data.deleted:
                continue
            value['axis'].append({
                'x_curve': child.graph_label_x,
                'y_curve': child.graph_label_y,
                'name': child.name,
                'group_by': child.graph_group_by,
                'graph_constraints': child.graph_constraints,
            })

        json_value = json.dumps(value)

        sp.new_upd_plot_template((None, json_value, None, None))

    def save_epure_template(self, index):
        folder = index.internalPointer()
        name = basic_funcs.get_text('Имя шаблона', 'Введите имя шаблона', 'Шаблон')

        value = {
            'name': name,
            'axis': []
        }
        for child in folder.children:
            if hasattr(child._data, 'deleted') and child._data.deleted:
                continue
            value['axis'].append({
                'x_curve': child.x_curve,
                'y_curve': child.y_curve,
                'name': child.name
            })

        json_value = json.dumps(value)

        sp.new_upd_plot_template((None, json_value, None, None))

    def apply_graph_template(self, index):
        item = index.internalPointer()
        graph_templates = sp.get_user_plot_templates()
        dialog = EditPlotTemplatesDialog(item, graph_templates)
        if dialog.exec_():  # Если произошло изменение данных
            graph_items = dialog.get_result()
            for g in graph_items:
                g.type_ = 'graph'
            self._add_item(tuple(graph_items), index, item._data.project_id, item)

    def change_property(self, prop, index):
        super().change_property(prop, index)

        if prop == 'name':
            self.model().update_external_graphs()
