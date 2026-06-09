from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtWidgets import QAction, QMenu

from app import basic_funcs, _menu
from app.basic_funcs import timing_decorator
from app.plugins.base_state.dialogs.column_settings import ColumnSettingsDialog
from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog
from app.plugins.base_state.widgets import TablePage1
from app.plugins.work_data.widgets.table import WorkDataTableView, WorkDataTableWidget
from db import sp
from db.tables import IMPORT_FILE_DATA


class WorkDataTablePage1(TablePage1):
    TABLE = WorkDataTableWidget

    @timing_decorator
    def __init__(self, cells, item, parent=None, main_window=None):
        super().__init__(cells, item, parent, main_window)
        # self.available_actions += ['_export_txt_template']
        self.add_toolbar_action('_export_txt_template',
                                QAction(QIcon(":export_excel.png"), 'Экспорт Excel', self,
                                        triggered=lambda: self.export_excel()))

    def show_row_menu(self, point):
        pass

    def show_column_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.column_menu, self, menu, _exclude=['_row_settings', '_remove_column', '_add_column'])
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def export_excel(self):
        filepath = basic_funcs.export_file(self.item.name.replace('"', '').replace("'", ''), "Экспорт испытания",
                                           "Файл Microsoft Excel (*.xlsx)")
        self.table.export(filepath)

    def get_row_db_object(self, param_name, prop_name, prop_value):
        return (
            0, self.parent().item._data.id_excel_file,
            self.parent().item._data.file_version, self.parent().item._data.excel_param_name, prop_name,
            None,
            None,
            None,
            prop_value, False, 0, self.parent().item._data.id_name,
        )

    def get_cell_db_object(self, param_name, prop_name, prop_value, curr_date):
        return (
            0, self.parent().item._data.project_id,
            int(self.parent().item.test_id), 0, param_name, prop_name,
            curr_date,
            None,
            None,
            prop_value, False, 0
        )

    def get_column_db_object(self, curr_date, prop_name, prop_value):

        return (
            0, self.parent().item._data.id_excel_file,
            self.parent().item._data.file_version,
            None,
            prop_name,
            curr_date,
            None,
            None,
            prop_value,
            False,
            -1,
        )

    def row_settings(self, index):
        item = self.table.itemFromIndex(index)
        row = item.key[0]
        dialog = RowSettingsDialog(row, item, parent=self)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()

    def column_settings(self, index):
        item = self.table.itemFromIndex(index)
        column = item.key[1]
        dialog = ColumnSettingsDialog(column, item, parent=self)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()

    def update_row_prop(self, name, prop_name, prop_value):
        if prop_name in self.table.rows[(name, None)]:
            record = self.table.rows[(name, None)][prop_name]
            record.prop_value = str(prop_value)
            _record = record.table_fit(IMPORT_FILE_DATA)
        else:
            record = self.table.rows[(name, None)]['type']
            record.param_prop_name = str(prop_name)
            record.prop_value = str(prop_value)
            _record = record.table_fit(IMPORT_FILE_DATA)
        success = sp.new_upd_excel_data_record(_record)
        if success:
            self.table.update_row_obj(name, prop_name, record)

    def update_column_prop(self, name, prop_name, prop_value):
        if prop_name in self.table.columns[(None, name)]:
            record = self.table.columns[(None, name)][prop_name]
            record.prop_value = str(prop_value)
            _record = record.table_fit(IMPORT_FILE_DATA)
        else:
            record = self.table.columns[(None, name)]['type']
            record.id_record = 0
            record.param_prop_name = str(prop_name)
            record.prop_value = str(prop_value)
            _record = record.table_fit(IMPORT_FILE_DATA)
        success = sp.new_upd_excel_data_record(_record)
        if success:
            self.table.update_column_obj(name, prop_name, record)


class WorkDataTableViewPage(WorkDataTablePage1):
    """Opt-in read-only Work Data page backed by QTableView."""

    TABLE = WorkDataTableView

    @timing_decorator
    def __init__(self, cells, item, parent=None, main_window=None):
        super().__init__(cells, item, parent, main_window)
        self.formula_panel.hide()
        for action_name in (
                'saveAction', 'boldAction', 'italicAction', 'sizeAction',
                'textColorAction', 'bgcolorAction', 'brokenAction'):
            action = getattr(self, action_name, None)
            if action is not None:
                action.setEnabled(False)

    def init_table(self, cells):
        """Set up model/view signals without QTableWidgetItem-only formula hooks."""
        self.table.load_table(cells)
        if hasattr(self.item, 'filters') and self.item.filters and (
                self.item.use_filters == 'True' or self.item.use_filters is True):
            self.table.apply_filters(self.item.filters)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_cell_menu)

        row_headers = self.table.verticalHeader()
        row_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        row_headers.customContextMenuRequested.connect(self.show_row_menu)

        column_headers = self.table.horizontalHeader()
        column_headers.setContextMenuPolicy(Qt.CustomContextMenu)
        column_headers.customContextMenuRequested.connect(self.show_column_menu)

        self.update_formula_context()
        self._set_formula_target(None)

    def show_cell_menu(self, point):
        # Cell actions currently depend on QTableWidgetItem/TableItem. The old
        # page remains the fallback for those editing-sensitive operations.
        pass

    def show_column_menu(self, point):
        # Column settings also depend on TableItem and are intentionally kept
        # on the old fallback until model/view editing parity is implemented.
        pass
