from app.plugins.base_state.widgets import TreeView
from app.plugins.work_data.dialogs import VersionControlDialog
from app.plugins.work_data.models import TestNode, FileNode
from app.plugins.work_data.widgets.tabs import WorkDataTab, FileTab
from db import sp


class WorkDataTreeView(TreeView):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('work_data', 'products_treeview')
        self.link_nodes_with_tabs({
            TestNode: WorkDataTab,
            FileNode: FileTab,
        })

    def connect_triggered_funcs(self, index):
        super(WorkDataTreeView, self).connect_triggered_funcs(index)
        self._connect_func('_version_control', self.version_control, index)

    def version_control(self, index):
        item = index.internalPointer()
        dialog = VersionControlDialog(item)
        if dialog.exec_():
            res = dialog.get_result()
            item.final_version = res

            temp_item = item._data
            temp_item.prod_prop = 'final_version'
            temp_item.prod_prop_value = res

            sp.new_update_product_from_record(temp_item.table_fit(item.scheme))
            #sp.session.commit()
