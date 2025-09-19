from app import app_logger
from app.plugins.base_state.plugin import BasePlugin
from app.plugins.eizm_dictionary.models import EizmDictionaryTreeModel
from app.plugins.eizm_dictionary.widgets import EizmDictionaryTreeView
from db import sp

logger = app_logger.get_logger(__name__)


class EizmDictionaryPlugin(BasePlugin):

    def __init__(self, parent):
        super().__init__(parent)
        self.eizm_treeview = None

    def tree_view(self):
        return self.eizm_treeview

    def activate(self):
        logger.info("Активирован режим Словаря единиц измерений.")
        model = EizmDictionaryTreeModel()
        eizms = sp.get_sprav_eizm_all()
        model.ini_tree([eizm for eizm in eizms if eizm.eizm_short != 'not_set'])
        self.eizm_treeview = EizmDictionaryTreeView(self._parent, main_window=self._parent)
        self.eizm_treeview.setModel(model)

        return True
