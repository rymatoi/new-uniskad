from app import app_logger
from app.plugins.base_state.plugin import BasePlugin
from app.plugins.synonym_dictionary.models import SynonymDictionaryTreeModel
from app.plugins.synonym_dictionary.widgets import SynonymDictionaryTreeView
from db import sp
from db.schemas import SpravName

logger = app_logger.get_logger(__name__)


class SynonymDictionaryPlugin(BasePlugin):

    def __init__(self, parent):
        super().__init__(parent)
        self.params_treeview = None

    def tree_view(self):
        return self.params_treeview

    def activate(self):
        logger.info("Активирован режим Словарей.")
        model = SynonymDictionaryTreeModel()
        params = sp.get_sprav_names_all()
        confirmed_nodes = SpravName({'id': -10, 'id_up': None, 'type_': 'confirmed_nodes'})
        unconfirmed_nodes = SpravName({'id': -20, 'id_up': None, 'type_': 'unconfirmed_nodes'})
        for param in params:
            if param.flag_permanent:
                if param.flag_synonim:
                    param.type_ = 'synonym'
                else:
                    param.type_ = 'standard'
                    param.id_up = -10
            else:
                param.type_ = 'unknown'
                param.id_up = -20

        model.ini_tree(params + [confirmed_nodes, unconfirmed_nodes])
        self.params_treeview = SynonymDictionaryTreeView(self._parent, main_window=self.main_window)
        self.params_treeview.setModel(model)

        return True
