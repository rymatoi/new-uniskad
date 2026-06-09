import time

from app import app_logger
from app.plugins.base_state.table_model import (LazyTableModel, LazyTableModelItem,
                                                ModelViewTable)
from app.plugins.base_state.widgets import TableWidget, TableItem
from db import sp
from db.tables import IMPORT_FILE_DATA

logger = app_logger.get_logger(__name__)


class WorkDataTableItem(TableItem):
    def update_cell(self, prop, value):
        tmp = self.get_prop_template(prop, value)
        self.tableWidget().need_update.append(tmp)
        self.add_prop(tmp)


class WorkDataTableWidget(TableWidget):
    TABLE_ITEM = WorkDataTableItem

    def get_update_cells(self):
        return [cell.table_fit(IMPORT_FILE_DATA) for cell in self.need_update]

    def load_table(self, db_objects):
        started = time.perf_counter()
        super().load_table(db_objects)
        logger.info("WorkDataTableWidget: loaded QTableWidget fallback in %.4f seconds",
                    time.perf_counter() - started)

    def update_table(self):
        success = sp.new_upd_excel_data_array(self.get_update_cells())
        if success:
            self.need_update = []


class WorkDataModelItem(LazyTableModelItem):
    pass


class WorkDataTableModel(LazyTableModel):
    ITEM_CLASS = WorkDataModelItem


class WorkDataTableView(ModelViewTable):
    """Opt-in lazy model/view Work Data table."""

    MODEL_CLASS = WorkDataTableModel
    TABLE_FIT = IMPORT_FILE_DATA
    SAVE_FUNCTION = staticmethod(sp.new_upd_excel_data_array)
