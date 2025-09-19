from app.plugins.base_state.widgets import TreeView


class EizmDictionaryTreeView(TreeView):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('eizm_dictionary', 'eizm_dictionary_treeview')
