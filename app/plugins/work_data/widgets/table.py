from app.plugins.base_state.widgets import TableWidget, TableItem
from db import sp
from db.tables import IMPORT_FILE_DATA


class WorkDataTableItem(TableItem):
    def update_cell(self, prop, value):
        tmp = self.get_prop_template(prop, value)
        self.tableWidget().need_update.append(tmp)
        self.add_prop(tmp)


class WorkDataTableWidget(TableWidget):
    TABLE_ITEM = WorkDataTableItem

    def get_update_cells(self):
        return [cell.table_fit(IMPORT_FILE_DATA) for cell in self.need_update]

    def update_table(self):
        success = sp.new_upd_excel_data_array(self.get_update_cells())
        if success:
            self.need_update = []
