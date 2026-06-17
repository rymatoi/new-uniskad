from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtWidgets import QAction, QMenu

from app import basic_funcs, _menu, app_logger
from app.basic_funcs import timing_decorator
from app.plugins.base_state.dialogs.column_settings import ColumnSettingsDialog
from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog
from app.plugins.base_state.table_model import clone_property_record
from app.plugins.base_state.widgets import TablePage1
from app.plugins.work_data.widgets.table import WorkDataTableView, WorkDataTableWidget
from db import sp
from db.tables import IMPORT_FILE_DATA

logger = app_logger.get_logger(__name__)


class WorkDataTablePage1(TablePage1):
    TABLE = WorkDataTableWidget
    structural_editing_enabled = False
    STRUCTURAL_ACTIONS = {
        '_add_row', '_remove_row', '_rename_row',
        '_add_column', '_remove_column', '_rename_column',
    }
    STRUCTURAL_ROW_PROPERTIES = {'name', 'row_npp', 'type'}
    STRUCTURAL_COLUMN_PROPERTIES = {'name', 'column_npp', 'type', 'date_time_izm'}

    @timing_decorator
    def __init__(self, cells, item, parent=None, main_window=None):
        super().__init__(cells, item, parent, main_window)
        # self.available_actions += ['_export_txt_template']
        self.available_actions = [action for action in self.available_actions
                                  if action not in self.STRUCTURAL_ACTIONS]
        self.add_toolbar_action('_export_txt_template',
                                QAction(QIcon(":export_excel.png"), 'Экспорт Excel', self,
                                        triggered=lambda: self.export_excel()))

    def show_row_menu(self, point):
        pass

    def show_column_menu(self, point):
        index = self.table.indexAt(point)
        menu = QMenu(self)
        _menu.init_menu(self.column_menu, self, menu,
                        _exclude=self.STRUCTURAL_ACTIONS | {'_row_settings'})
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def export_excel(self):
        filepath = basic_funcs.export_file(self.item.name.replace('"', '').replace("'", ''), "Экспорт испытания",
                                           "Файл Microsoft Excel (*.xlsx)")
        if not filepath:
            logger.info("WorkData export cancelled by user")
            return
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
        item = (self.table.ensureItem(index) if hasattr(self.table, 'ensureItem')
                else self.table.itemFromIndex(index))
        row = item.key[0]
        dialog = RowSettingsDialog(row, item, parent=self)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()

    def column_settings(self, index):
        item = (self.table.ensureItem(index) if hasattr(self.table, 'ensureItem')
                else self.table.itemFromIndex(index))
        column = item.key[1]
        dialog = ColumnSettingsDialog(column, item, parent=self)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()

    def _reject_structural_edit(self):
        logger.warning('Work Data structural editing is disabled')
        return False

    def connect_triggered_funcs(self, index):
        """Connect only non-structural actions, even when DB menu data contains them."""
        self._connect_func('_row_settings', self.row_settings, index)
        self._connect_func('_column_settings', self.column_settings, index)

    def add_row(self, index):
        return self._reject_structural_edit()

    def add_column(self, index):
        return self._reject_structural_edit()

    def remove_row(self, index):
        return self._reject_structural_edit()

    def remove_column(self, index):
        return self._reject_structural_edit()

    def remove_rows(self, index):
        return self._reject_structural_edit()

    def remove_columns(self, index):
        return self._reject_structural_edit()

    def rename_row(self, index):
        return self._reject_structural_edit()

    def rename_column(self, index):
        return self._reject_structural_edit()

    @staticmethod
    def _property_template(properties):
        return properties.get('type') or next(iter(properties.values()), None)

    def update_row_prop(self, name, prop_name, prop_value):
        if prop_name in self.STRUCTURAL_ROW_PROPERTIES:
            return self._reject_structural_edit()
        properties = self.table.rows.get((name, None), {})
        if prop_name in properties:
            record = properties[prop_name]
            record.prop_value = str(prop_value)
        else:
            template = self._property_template(properties)
            if template is None:
                logger.warning('Cannot update Work Data row property %s: row %r has no metadata',
                               prop_name, name)
                return False
            record = clone_property_record(template, prop_name, prop_value)
        success = sp.new_upd_excel_data_record(record.table_fit(IMPORT_FILE_DATA))
        if success:
            self.table.update_row_obj(name, prop_name, record)
        return bool(success)

    def update_column_prop(self, name, prop_name, prop_value):
        if prop_name in self.STRUCTURAL_COLUMN_PROPERTIES:
            return self._reject_structural_edit()
        properties = self.table.columns.get((None, name), {})
        if prop_name in properties:
            record = properties[prop_name]
            record.prop_value = str(prop_value)
        else:
            template = self._property_template(properties)
            if template is None:
                logger.warning('Cannot update Work Data column property %s: column %r has no metadata',
                               prop_name, name)
                return False
            record = clone_property_record(template, prop_name, prop_value)
        success = sp.new_upd_excel_data_record(record.table_fit(IMPORT_FILE_DATA))
        if success:
            self.table.update_column_obj(name, prop_name, record)
        return bool(success)


class WorkDataTableViewPage(WorkDataTablePage1):
    """Opt-in Work Data page backed by the parity model/view implementation."""

    TABLE = WorkDataTableView

    def show_row_menu(self, point):
        # The model/view path exposes the loaded row menu even though the
        # fallback Work Data page historically suppresses it.
        row = self.table.verticalHeader().logicalIndexAt(point)
        column = max(self.table.currentColumn(), 0)
        index = self.table.model().index(row, column)
        menu = QMenu(self)
        _menu.init_menu(self.row_menu, self, menu,
                        _exclude=self.STRUCTURAL_ACTIONS | {'_recalculate_eizm'})
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def show_column_menu(self, point):
        column = self.table.horizontalHeader().logicalIndexAt(point)
        row = max(self.table.currentRow(), 0)
        index = self.table.model().index(row, column)
        menu = QMenu(self)
        _menu.init_menu(self.column_menu, self, menu,
                        _exclude=self.STRUCTURAL_ACTIONS | {'_row_settings'})
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def show_cell_menu(self, point):
        if self.table.indexAt(point).isValid():
            TablePage1.show_cell_menu(self, point)
            return
        menu = QMenu(self)
        _menu.init_menu(self.table_menu, self, menu)
        menu.popup(QCursor.pos())
