import time

from PySide2.QtCore import Qt

from app import app_logger
from app.plugins.base_state.table_model import (LazyTableModel, LazyTableModelItem,
                                                ModelViewTable)
from app.plugins.base_state.widgets import TableWidget, TableItem
from db import sp
from db.tables import PROJECT_DATA

logger = app_logger.get_logger(__name__)


class ProjectTableItem(TableItem):
    def update_cell(self, prop, value):
        tmp = self.get_prop_template(prop, value)
        self.tableWidget().need_update.append(tmp)
        self.add_prop(tmp)


class ProjectTableWidget(TableWidget):
    TABLE_ITEM = ProjectTableItem

    def set_vertical_headers(self):
        header_names = []
        for row in self.ord_rows:
            unit = self.rows[(row, None)].get('eizm_short')
            header_names.append(f'{row}, {unit.prop_value}' if unit and unit.prop_value != 'not_set' else row)
        self.setVerticalHeaderLabels(header_names)

    def get_update_cells(self):
        return [cell.table_fit(PROJECT_DATA) for cell in self.need_update]

    def update_table(self):
        started = time.perf_counter()
        success = sp.new_upd_project_data_array(self.get_update_cells())
        logger.info("ProjectTableWidget: save/update path completed in %.4f seconds",
                    time.perf_counter() - started)
        if success:
            self._parent._parent._parent.model().update_external_graphs()
            self.need_update = []


class ProjectModelItem(LazyTableModelItem):
    pass


class ProjectTableModel(LazyTableModel):
    ITEM_CLASS = ProjectModelItem

    def headerData(self, section, orientation, role=None):
        if role is None:
            role = Qt.DisplayRole
        if role == Qt.DisplayRole and orientation == Qt.Vertical and 0 <= section < len(self.ord_rows):
            row = self.ord_rows[section]
            unit = self.rows.get((row, None), {}).get('eizm_short')
            return f'{row}, {unit.prop_value}' if unit and unit.prop_value != 'not_set' else row
        return super().headerData(section, orientation, role)


class ProjectTableView(ModelViewTable):
    """Opt-in lazy model/view Project table."""

    MODEL_CLASS = ProjectTableModel
    TABLE_FIT = PROJECT_DATA
    SAVE_FUNCTION = staticmethod(sp.new_upd_project_data_array)

    def update_table(self):
        started = time.perf_counter()
        deleted = [record for record in self.need_update if record.deleted]
        updated = [record for record in self.need_update if not record.deleted]

        deleted_success = (not deleted or sp.del_restore_project_data_array(
            [record.table_fit(self.TABLE_FIT) for record in deleted]))
        updated_success = (deleted_success and
                           (not updated or self.SAVE_FUNCTION(
                               [record.table_fit(self.TABLE_FIT) for record in updated])))
        success = deleted_success and updated_success
        logger.info(
            "ProjectTableView: save/update path completed in %.4f seconds "
            "(saved deleted records=%d/%d, saved updated records=%d/%d, success=%s)",
            time.perf_counter() - started, len(deleted) if deleted_success else 0,
            len(deleted), len(updated) if updated_success else 0, len(updated), success)
        if success:
            self.need_update = []
            self.post_save()
        return success

    def post_save(self):
        try:
            self._parent._parent._parent.model().update_external_graphs()
        except AttributeError:
            logger.warning('ProjectTableView: external graph update target is unavailable')
