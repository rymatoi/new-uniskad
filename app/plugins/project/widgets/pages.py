from datetime import datetime
from PySide2.QtGui import QIcon, QPixmap, QPainter, Qt
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import QAction
from pyqtgraph import InfiniteLine

from app import app_logger, basic_funcs
from app.basic_funcs import export_file
from app.plugins.base_state.dialogs.column_settings import ColumnSettingsDialog
from app.plugins.base_state.dialogs.export_txt_template import ExportTxtDialog
from app.plugins.base_state.dialogs.manage_user_formulas import ManageUserFormulasDialog
from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog
from app.plugins.base_state.widgets import TablePage1
from app.plugins.project.dialogs.edit_plane import EditPlaneDialog
from app.plugins.project.plot.plot_page import PlotPage
from app.plugins.project.widgets.table import ProjectTableWidget

from app.utils import convert, excel
from db import sp
from db.tables import PROJECT_DATA

logger = app_logger.get_logger(__name__)


class ProjectTablePage1(TablePage1):
    TABLE = ProjectTableWidget

    def __init__(self, cells, item, parent=None, main_window=None):

        super().__init__(cells, item, parent, main_window)

        self.add_toolbar_action('_edit_formula_list', QAction(QIcon(":formula.png"), 'Список шаблонных формул', self,
                                                              triggered=lambda: self.edit_formula_list()))
        self.add_toolbar_action('_export_txt_template',
                                QAction(QIcon(":export_txt_template.png"), 'Экспорт по шаблону TXT', self,
                                        triggered=lambda: self.export_txt_template()))

        self.add_toolbar_action('_export_excel',
                                QAction(QIcon(":export_excel.png"), 'Экспорт Excel', self,
                                        triggered=lambda: self.export_excel()))

    def export_excel(self):
        filepath = basic_funcs.export_file(self.item.name.replace('"', '').replace("'", ''), "Экспорт испытания",
                                           "Файл Microsoft Excel (*.xlsx)")
        self.table.export(filepath)

    def export_txt_template(self):

        if len(self.table.selectedIndexes()) == 0:
            self.table.selectAll()

        dialog = ExportTxtDialog(self.table)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()

    def get_row_db_object(self, param_name, prop_name, prop_value):
        return (
            0, self.parent().item._data.project_id,
            int(self.parent().item.test_id), 0, param_name, prop_name,
            None,
            None,
            None,
            str(prop_value), False, 0
        )

    def get_cell_db_object(self, param_name, prop_name, prop_value, curr_date):
        return (
            0, self.parent().item._data.project_id,
            int(self.parent().item.test_id), 0, param_name, prop_name,
            curr_date,
            None,
            None,
            str(prop_value), False, 0
        )

    def get_column_db_object(self, curr_date, prop_name, prop_value):
        return (
            0, self.parent().item._data.project_id,
            int(self.parent().item.test_id), 0, None, prop_name,
            curr_date,
            None,
            None,
            str(prop_value), False, 0
        )

    def bulk_update_cells(self, cells, prop_name, prop_value):
        result_list = []
        for cell in cells:
            c = cell.cell['type']
            result_list.append(self.get_cell_db_object(c.excel_param_name, prop_name, prop_value, c.date_time_izm))
        sp.new_upd_project_data_array(result_list)

    def add_row(self, index, name=None, formula=None):
        # item = self.table.itemFromIndex(index)
        max_row = self.table.ord_rows[-1]
        max_row_npp = self.table.get_row_npp(max_row)
        if name is None:
            new_param_name = basic_funcs.get_text('Добавление строки', 'Введите название параметра строки:',
                                                  'Новая строка')
        else:
            new_param_name = name

        if new_param_name in self.table.ord_rows:
            return

        if new_param_name:
            cells = [self.get_row_db_object(new_param_name, 'type', 'row'),
                     self.get_row_db_object(new_param_name, 'row_npp', str(max_row_npp)),
                     self.get_row_db_object(new_param_name, 'name', str(new_param_name))]
            for i in self.table.ord_columns:
                cells.append(self.get_cell_db_object(new_param_name, 'value', '0', i))
                cells.append(self.get_cell_db_object(new_param_name, 'type', 'cell', i))
                if formula:
                    cells.append(self.get_cell_db_object(new_param_name, 'formula', str(formula), i))
            new_cells = sp.new_project_data_array(cells)
            self.table.add_row(new_cells)
            self.update_formula_context()
            self._set_formula_target(self.table.currentItem())

    def remove_row(self, index):
        if not index.isValid():
            return
        item = self.table.itemFromIndex(index)
        obj_list = []
        cells_to_delete = []
        for c in self.table.ord_columns:
            cell = self.table.table[item.key[0], c]
            cells_to_delete.append((item.key[0], c))
            for prop in cell.values():
                prop.deleted = True
                obj_list.append(prop)

        for prop in self.table.rows[item.key[0], None].values():
            prop.deleted = True
            obj_list.append(prop)
        result = sp.del_restore_project_data_array(
            [obj.table_fit(PROJECT_DATA) for obj in obj_list])

        if result:
            self.table.ord_rows.remove(item.key[0])
            del self.table.rows[item.key[0], None]
            self.table.removeRow(item.row())
            for cell in cells_to_delete:
                del self.table.table[cell]
            self.update_formula_context()
            self._set_formula_target(self.table.currentItem())

    def add_column(self, index):
        # current_date = datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")
        current_date = datetime.now()
        column_count = len(self.table.ord_columns)
        column = self.get_column_db_object(current_date, 'type', 'column')
        column_npp = self.get_column_db_object(current_date, 'column_npp', str(column_count))

        cells = []
        for param_name in self.table.ord_rows:
            cell_type = self.get_cell_db_object(param_name, 'type', 'cell', current_date)
            cell_value = self.get_cell_db_object(param_name, 'value', '0', current_date)
            cells += [cell_type, cell_value]

        new_columns = sp.new_project_data_array(
            [column,
             column_npp] + cells)

        self.table.add_column(new_columns)
        self.update_formula_context()
        self._set_formula_target(self.table.currentItem())

    def remove_column(self, index):
        if not index.isValid():
            return
        item = self.table.itemFromIndex(index)
        obj_list = []
        for c in self.table.ord_rows:
            for prop in self.table.table[c, item.key[1]].values():
                prop.deleted = True
                obj_list.append(prop)
        for prop in self.table.columns[None, item.key[1]].values():
            prop.deleted = True
            obj_list.append(prop)
        result = sp.del_restore_project_data_array(
            [obj.table_fit(PROJECT_DATA) for obj in obj_list])

        if result:
            self.table.removeColumn(item.column())
            self.table.ord_columns.remove(item.key[1])
            del self.table.columns[None, item.key[1]]
            self._set_formula_target(self.table.currentItem())

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
            record = record.table_fit(PROJECT_DATA)
        else:
            record = self.get_row_db_object(name, prop_name, str(prop_value))
        success = sp.new_upd_project_data_record(record)
        if success:
            self.table.update_row_obj(name, prop_name, success)

    def update_column_prop(self, name, prop_name, prop_value):
        if prop_name in self.table.columns[(None, name)]:
            record = self.table.columns[(None, name)][prop_name]
            record.prop_value = str(prop_value)
            record = record.table_fit(PROJECT_DATA)
        else:
            record = self.get_column_db_object(name, prop_name, str(prop_value))
        success = sp.new_upd_project_data_record(record)
        if success:
            self.table.update_column_obj(name, prop_name, success)

    def edit_formula_list(self):
        dialog = ManageUserFormulasDialog(self, self.mw)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()


class ProjectPlotPage(PlotPage):
    def __init__(self, item, parent=None, main_window=None):
        super().__init__(item, parent, main_window)

        # Определяем действия тулбара в виде словаря
        toolbar_actions = {
            '_save': {
                'icon': ':diskette.png',
                'text': 'Сохранить изменения',
                'triggered': self.save_changes
            },
            '_plane_settings': {
                'icon': ':settings.png',
                'text': 'Настройка графика',
                'triggered': self.plane_settings
            },
            '_printer': {
                'icon': ':printer.png',
                'text': 'Печать на принтере',
                'triggered': self.print_on_printer
            },
            '_export_emf': {
                'icon': ':emf.png',
                'text': 'Экспорт в EMF',
                'triggered': self.export_emf
            },
            '_export_excel': {
                'icon': ':export_excel.png',
                'text': 'Экспорт в EXCEL',
                'triggered': self.export_excel
            }
        }

        # Создаем действия из словаря
        for action_name, props in toolbar_actions.items():
            action = QAction(QIcon(props['icon']), props['text'], self)

            if 'triggered' in props:
                action.triggered.connect(props['triggered'])
            if 'toggled' in props:
                action.setCheckable(True)
                action.toggled.connect(props['toggled'])

            self.add_toolbar_action(action_name, action)

    def save_changes(self):
        self.plotView.commit_changes()

    def plane_settings(self):
        dialog = EditPlaneDialog(self.item)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()
            self.plotView.refresh()

    def export_excel(self):
        file_path = export_file("123.xlsx", "Экспорт графика", "Файл EXCEL (*.xlsx)")
        self.plotView.export_to_excel(file_path)

    def export_emf(self):
        file_path = export_file(self.plotView.item.data(), "Экспорт графика", "Файл EMF (*.emf)")
        self.plotView.export_to_emf(file_path)

    def print_on_printer(self):
        pixmap = QPixmap(self.plotView.grab())

        # Create a printer dialog
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_():
            painter = QPainter(printer)
            painter.begin(self)
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
