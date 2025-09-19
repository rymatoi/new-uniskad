from app.plugins.base_state.widgets import TableWidget, TableItem
from db import sp
from db.tables import PROJECT_DATA


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
            if 'eizm_short' in self.rows[(row, None)].keys() and self.rows[(row, None)][
                'eizm_short'].prop_value != 'not_set':
                header_names.append(f'{row}, {self.rows[(row, None)]["eizm_short"].prop_value}')
            else:
                header_names.append(row)
        self.setVerticalHeaderLabels(header_names)

    def get_update_cells(self):
        return [cell.table_fit(PROJECT_DATA) for cell in self.need_update]

    def update_table(self):
        success = sp.new_upd_project_data_array(self.get_update_cells())
        if success:
            self._parent._parent._parent.model().update_external_graphs()
            self.need_update = []
