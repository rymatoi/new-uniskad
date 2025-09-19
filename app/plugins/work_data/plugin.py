from app import app_logger
from app.plugins.base_state.plugin import BasePlugin
from app.plugins.work_data.models import WorkDataTreeModel
from app.plugins.work_data.widgets.tree import WorkDataTreeView
from db import sp

logger = app_logger.get_logger(__name__)


class WorkDataPlugin(BasePlugin):

    def __init__(self, parent):
        super().__init__(parent)
        self.products_treeview = None

    def tree_view(self):
        return self.products_treeview

    def activate(self):
        logger.info("Активирован режим Рабочие данные.")
        model = WorkDataTreeModel()
        model.root_id = 1
        products = sp.get_all_products()
        product_types = sp.get_product_types()
        product_types_dict = {type_.id_prod_type: type_.prod_type for type_ in product_types}

        for product in products:
            product.type_ = product_types_dict[product.id_ptype]

        model.ini_tree(products)
        self.products_treeview = WorkDataTreeView(self._parent, main_window=self._parent)
        self.products_treeview.setModel(model)

        return True
