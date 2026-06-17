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
        if not self.need_update:
            return True
        started = time.perf_counter()
        pending = list(self.need_update)
        success = sp.new_upd_project_data_array([cell.table_fit(PROJECT_DATA) for cell in pending])
        logger.info("ProjectTableWidget: save/update path completed in %.4f seconds "
                    "(saved updated records=%d/%d, success=%s)",
                    time.perf_counter() - started, len(pending) if success else 0, len(pending), success)
        if success:
            changed_params = {getattr(record, 'excel_param_name', None) for record in pending}
            changed_params.discard(None)
            self.need_update = []
            if pending and hasattr(self._parent, 'notify_project_data_changed'):
                self._parent.notify_project_data_changed(self._parent._project_id(), changed_params or None)
        return success


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
        if not self.need_update:
            return True
        started = time.perf_counter()
        pending = list(self.need_update)
        deleted = [record for record in pending if record.deleted]
        updated = [record for record in pending if not record.deleted]

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
            changed_params = {getattr(record, 'excel_param_name', None) for record in pending}
            changed_params.discard(None)
            self.need_update = []
            if (deleted or updated) and hasattr(self._parent, 'notify_project_data_changed'):
                self._parent.notify_project_data_changed(self._parent._project_id(), changed_params or None)
            self.post_save()
        return success

    def post_save(self):
        pass
