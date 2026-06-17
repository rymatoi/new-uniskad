from datetime import datetime
from PySide2.QtCore import QTimer
from PySide2.QtGui import QCursor, QIcon, QPixmap, QPainter, Qt
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import QAction, QMenu, QMessageBox
from pyqtgraph import InfiniteLine

from app import _menu, app_logger, basic_funcs
from app.basic_funcs import export_file
from app.plugins.base_state.dialogs.column_settings import ColumnSettingsDialog
from app.plugins.base_state.dialogs.export_txt_template import ExportTxtDialog
from app.plugins.base_state.dialogs.manage_user_formulas import ManageUserFormulasDialog
from app.plugins.base_state.dialogs.row_settings import RowSettingsDialog
from app.feature_flags import is_feature_enabled
from app.plugins.base_state.widgets import TablePage1
from app.plugins.project.dialogs.edit_plane import EditPlaneDialog
from app.plugins.project.plot.plot_page import PlotPage
from app.plugins.project.widgets.table import ProjectTableView, ProjectTableWidget
from app.plugins.project.utils_ import (
    clear_project_param_cache,
    parse_json_or_literal_value,
    resolve_project_param_cache_project_id,
)

from app.utils import convert, excel
from db import sp
from db.tables import PROJECT_DATA

logger = app_logger.get_logger(__name__)


class ProjectTablePage1(TablePage1):
    TABLE = ProjectTableWidget

    def __init__(self, cells, item, parent=None, main_window=None):
        use_table_view = is_feature_enabled('UNISKAD_PROJECT_TABLE_VIEW')
        self.TABLE = ProjectTableView if use_table_view else ProjectTableWidget
        logger.info("Project table implementation: %s", self.TABLE.__name__)
        self._autosave_in_progress = False
        self._autosave_scheduled = False
        self._pending_autosave_changed_params = set()
        super().__init__(cells, item, parent, main_window)

        if hasattr(self, "saveAction"):
            self.toolbar.removeAction(self.saveAction)
            self.saveAction.deleteLater()
            del self.saveAction

        self.add_toolbar_action('_edit_formula_list', QAction(QIcon(":formula.png"), 'Список шаблонных формул', self,
                                                              triggered=lambda: self.edit_formula_list()))
        self.add_toolbar_action('_export_txt_template',
                                QAction(QIcon(":export_txt_template.png"), 'Экспорт по шаблону TXT', self,
                                        triggered=lambda: self.export_txt_template()))

        self.add_toolbar_action('_export_excel',
                                QAction(QIcon(":export_excel.png"), 'Экспорт Excel', self,
                                        triggered=lambda: self.export_excel()))


    def _opened_graph_tabs(self):
        candidates = []
        parent_tab = self.parent()
        if parent_tab is not None:
            candidates.append(getattr(parent_tab, '_parent', None))
        candidates.extend([
            getattr(self, '_parent', None),
            getattr(self, 'mw', None),
            getattr(parent_tab, 'main_window', None) if parent_tab is not None else None,
        ])

        seen_sources = set()
        tabs = []
        seen_tabs = set()
        for source in candidates:
            if source is None or id(source) in seen_sources:
                continue
            seen_sources.add(id(source))
            get_tabs = getattr(source, 'get_opened_tabs', None)
            if callable(get_tabs):
                try:
                    source_tabs = list(get_tabs())
                except Exception:
                    logger.debug('Could not read opened tabs from %s', type(source).__name__, exc_info=True)
                    continue
                for tab in source_tabs:
                    if id(tab) not in seen_tabs:
                        seen_tabs.add(id(tab))
                        tabs.append(tab)
            opened_tabs = getattr(source, '_opened_tabs', None)
            if isinstance(opened_tabs, dict):
                for tab in opened_tabs.values():
                    if id(tab) not in seen_tabs:
                        seen_tabs.add(id(tab))
                        tabs.append(tab)
        return tabs

    def _cache_project_id(self):
        return resolve_project_param_cache_project_id(item=self.item) or self._project_id()

    def _graph_cache_project_id(self, graph_item):
        return resolve_project_param_cache_project_id(item=graph_item)

    @staticmethod
    def _normalize_param_name(value):
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _graph_depends_on_params(self, graph_item, changed_params):
        graph_id = getattr(getattr(graph_item, '_data', None), 'id', None)
        if changed_params is None:
            logger.debug(
                'Graph dependency check: graph_id=%s, dependencies=ALL, changed_params=None, depends=True',
                graph_id,
            )
            return True

        changed = {self._normalize_param_name(param) for param in changed_params}
        changed.discard(None)
        dependencies = {
            self._normalize_param_name(getattr(graph_item, 'graph_label_x', None)),
            self._normalize_param_name(getattr(graph_item, 'graph_label_y', None)),
        }
        dependencies.discard(None)

        constraints = getattr(graph_item, 'graph_constraints', None)
        parsed_constraints = parse_json_or_literal_value(constraints, default=None)
        if isinstance(parsed_constraints, dict):
            dependencies.update(
                dep for dep in (self._normalize_param_name(key) for key in parsed_constraints.keys()) if dep
            )
        elif isinstance(parsed_constraints, (list, tuple, set)):
            for constraint in parsed_constraints:
                if isinstance(constraint, dict):
                    for key in ('x', 'param', 'parameter', 'name'):
                        dep = self._normalize_param_name(constraint.get(key))
                        if dep:
                            dependencies.add(dep)
                else:
                    dep = self._normalize_param_name(constraint)
                    if dep:
                        dependencies.add(dep)

        result = bool(dependencies & changed)
        logger.debug(
            'Graph dependency check: graph_id=%s, dependencies=%s, changed_params=%s, depends=%s',
            graph_id, dependencies, changed, result,
        )
        return result

    def notify_project_data_changed(self, project_id, changed_params=None):
        table_cache_project_id = self._cache_project_id()
        logger.info('Project data changed: test_project_id=%s, table_cache_project_id=%s, changed_params=%s',
                    project_id, table_cache_project_id, changed_params)
        if table_cache_project_id is None:
            logger.warning('Project data changed but table cache project id could not be determined; clearing all project param cache')
            clear_project_param_cache()
        else:
            clear_project_param_cache(table_cache_project_id)

        opened_tabs = self._opened_graph_tabs()
        logger.debug('Project data changed: opened tabs inspected=%s', len(opened_tabs))
        refreshed_graph_ids = set()
        for tab in opened_tabs:
            tab_item = getattr(tab, 'item', None)
            logger.debug(
                'Opened tab inspected: tab=%s, tab_class=%s, item=%s, item_type=%s, item_id=%s, title=%s',
                tab,
                type(tab).__name__,
                tab_item,
                getattr(tab_item, 'internal_type', lambda: None)() if tab_item else None,
                getattr(getattr(tab_item, '_data', None), 'id', None),
                tab.windowTitle() if hasattr(tab, 'windowTitle') else None,
            )

            graph_item = tab_item
            graph_id = getattr(getattr(graph_item, '_data', None), 'id', None) if graph_item is not None else None
            if graph_item is None or getattr(graph_item, 'internal_type', lambda: None)() != 'graph':
                logger.debug('Skipping opened tab because it is not a graph: tab_class=%s, item_id=%s',
                            type(tab).__name__, graph_id)
                continue
            graph_cache_project_id = self._graph_cache_project_id(graph_item)
            logger.debug(
                'Graph cache project id resolved: graph_id=%s, graph_cache_project_id=%s',
                graph_id, graph_cache_project_id,
            )
            if not self._normalize_param_name(getattr(graph_item, 'graph_label_x', None)) or not self._normalize_param_name(getattr(graph_item, 'graph_label_y', None)):
                logger.warning('Skipping graph because axis params are empty: graph_id=%s', graph_id)
                continue
            depends = self._graph_depends_on_params(graph_item, changed_params)
            same_cache_id_known = table_cache_project_id is not None and graph_cache_project_id is not None
            if same_cache_id_known and graph_cache_project_id != table_cache_project_id:
                if not depends:
                    logger.info(
                        'Skipping graph due to cache project mismatch and no dependency match: graph_id=%s, graph_cache_project_id=%s, table_cache_project_id=%s',
                        graph_id, graph_cache_project_id, table_cache_project_id,
                    )
                    continue
                logger.info(
                    'Graph cache project mismatch detected, but dependency matched; refreshing anyway: graph_id=%s, graph_cache_project_id=%s, table_cache_project_id=%s',
                    graph_id, graph_cache_project_id, table_cache_project_id,
                )
            if not depends or graph_id in refreshed_graph_ids:
                continue
            if graph_cache_project_id is not None and graph_cache_project_id != table_cache_project_id:
                clear_project_param_cache(graph_cache_project_id)

            page = getattr(tab, 'plot_page', None)
            plot_view = getattr(page, 'plotView', None)
            if plot_view is None:
                widget = tab.widget() if hasattr(tab, 'widget') else None
                plot_view = getattr(widget, 'plotView', None)
            if plot_view is None:
                logger.warning(
                    'Dependent graph tab found but plotView is missing: graph_id=%s, tab_class=%s',
                    graph_id, type(tab).__name__,
                )
                continue
            logger.info(
                'Refreshing dependent graph: graph_id=%s, graph_name=%s, changed_params=%s',
                graph_id,
                (getattr(graph_item, 'graph_name', None) or getattr(graph_item, 'name', None) or graph_item.data() or (tab.windowTitle() if hasattr(tab, 'windowTitle') else None)),
                changed_params,
            )
            refreshed_graph_ids.add(graph_id)
            plot_view.reload_data_processor()
            plot_view.refresh()

    def _project_id(self):
        return getattr(getattr(self.item, '_data', None), 'project_id', None)

    def _autosave_pending_table_changes(self, changed_params=None):
        if getattr(self, '_autosave_in_progress', False):
            self._autosave_scheduled = True
            return
        if not getattr(self.table, 'need_update', None):
            return
        self._autosave_in_progress = True
        try:
            self.table.update_table()
        finally:
            self._autosave_in_progress = False
            if getattr(self, '_autosave_scheduled', False):
                self._autosave_scheduled = False
                self._queue_autosave_pending_table_changes(getattr(self, '_pending_autosave_changed_params', None))

    def _queue_autosave_pending_table_changes(self, changed_params=None):
        if not getattr(self.table, 'need_update', None):
            return
        pending_params = getattr(self, '_pending_autosave_changed_params', set())
        if changed_params is None:
            self._pending_autosave_changed_params = None
        elif pending_params is not None:
            pending_params.update(changed_params)
            self._pending_autosave_changed_params = pending_params
        if getattr(self, '_autosave_scheduled', False):
            return
        self._autosave_scheduled = True

        def run_autosave():
            self._autosave_scheduled = False
            params = getattr(self, '_pending_autosave_changed_params', None)
            self._pending_autosave_changed_params = set()
            self._autosave_pending_table_changes(params or None)

        QTimer.singleShot(0, run_autosave)

    def on_table_item_changed(self, item):
        super().on_table_item_changed(item)
        param_name = getattr(getattr(item, 'key', None), '__getitem__', lambda i: None)(0) if getattr(item, 'key', None) else None
        self._queue_autosave_pending_table_changes({param_name} if param_name else None)

    def show_row_menu(self, point):
        row = self.table.verticalHeader().logicalIndexAt(point)
        column = max(self.table.currentColumn(), 0)
        index = self.table.model().index(row, column)
        menu = QMenu(self)
        _menu.init_menu(self.row_menu, self, menu, _exclude=['_rename_row', '_recalculate_eizm'])
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def show_column_menu(self, point):
        column = self.table.horizontalHeader().logicalIndexAt(point)
        row = max(self.table.currentRow(), 0)
        index = self.table.model().index(row, column)
        menu = QMenu(self)
        _menu.init_menu(self.column_menu, self, menu)
        self.connect_triggered_funcs(index)
        menu.popup(QCursor.pos())

    def clear_param_cache(self):
        clear_project_param_cache(self._cache_project_id())

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
        self.notify_project_data_changed(self._project_id(), {c.cell['type'].excel_param_name for c in cells})

    def add_row(self, index, name=None, formula=None):
        ord_rows = list(self.table.ord_rows)
        insert_position = len(ord_rows)
        rows_to_shift = []

        if ord_rows:
            if index is not None and index.isValid():
                item = self.table.itemFromIndex(index)
                if item is not None and item.key[0] in ord_rows:
                    insert_position = ord_rows.index(item.key[0]) + 1

            if insert_position < len(ord_rows):
                next_row_name = ord_rows[insert_position]
                new_row_npp = self.table.get_row_npp(next_row_name)
                if new_row_npp is None:
                    new_row_npp = insert_position
                rows_to_shift = ord_rows[insert_position:]
            else:
                last_row_name = ord_rows[-1]
                last_row_npp = self.table.get_row_npp(last_row_name)
                if last_row_npp is None:
                    last_row_npp = len(ord_rows) - 1
                new_row_npp = last_row_npp + 1
        else:
            insert_position = 0
            new_row_npp = 0

        if name is None:
            new_param_name = basic_funcs.get_text('Добавление строки', 'Введите название параметра строки:',
                                                  'Новая строка')
        else:
            new_param_name = name

        if new_param_name in self.table.ord_rows:
            return

        if new_param_name:
            cells = [self.get_row_db_object(new_param_name, 'type', 'row'),
                     self.get_row_db_object(new_param_name, 'row_npp', str(new_row_npp)),
                     self.get_row_db_object(new_param_name, 'name', str(new_param_name))]
            for i in self.table.ord_columns:
                cells.append(self.get_cell_db_object(new_param_name, 'value', '0', i))
                cells.append(self.get_cell_db_object(new_param_name, 'type', 'cell', i))
                if formula:
                    cells.append(self.get_cell_db_object(new_param_name, 'formula', str(formula), i))
            new_cells = sp.new_project_data_array(cells)
            self.table.add_row(new_cells, insert_position)

            new_row_obj = self.table.rows.get((new_param_name, None), {}).get('row_npp')
            if new_row_obj is not None:
                new_row_obj.prop_value = str(new_row_npp)
                if hasattr(new_row_obj, 'npp'):
                    new_row_obj.npp = new_row_npp

            if rows_to_shift:
                update_data = []
                next_npp_value = new_row_npp + 1
                for row_name in rows_to_shift:
                    row_props = self.table.rows.get((row_name, None), {})
                    row_npp_obj = row_props.get('row_npp')
                    if row_npp_obj is None:
                        continue
                    row_npp_obj.prop_value = str(next_npp_value)
                    if hasattr(row_npp_obj, 'npp'):
                        row_npp_obj.npp = next_npp_value
                    update_data.append(row_npp_obj.table_fit(PROJECT_DATA))
                    next_npp_value += 1
                if update_data:
                    sp.new_upd_project_data_array(update_data)
            self.notify_project_data_changed(self._project_id(), None)

            self.update_formula_context()
            self._set_formula_target(self.table.currentItem())

    def remove_row(self, index):
        if not index.isValid():
            return
        if isinstance(self.table, ProjectTableView):
            row = index.row()
            if not 0 <= row < len(self.table.ord_rows):
                return
            row_key = self.table.ord_rows[row]
            self.table.queue_row_deletion(row_key)
            if self.table.removeRow(row):
                self.update_formula_context()
                self._set_formula_target(self.table.currentItem())
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
            self.notify_project_data_changed(self._project_id(), {item.key[0]})
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
        self.notify_project_data_changed(self._project_id(), None)
        self.update_formula_context()
        self._set_formula_target(self.table.currentItem())

    def remove_column(self, index):
        if not index.isValid():
            return
        if isinstance(self.table, ProjectTableView):
            column = index.column()
            if not 0 <= column < len(self.table.ord_columns):
                return
            column_key = self.table.ord_columns[column]
            self.table.queue_column_deletion(column_key)
            if self.table.removeColumn(column):
                self._set_formula_target(self.table.currentItem())
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
            self.notify_project_data_changed(self._project_id(), None)
            self.table.ord_columns.remove(item.key[1])
            del self.table.columns[None, item.key[1]]
            self._set_formula_target(self.table.currentItem())

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

    def update_row_prop(self, name, prop_name, prop_value):
        if prop_name in self.table.rows[(name, None)]:
            record = self.table.rows[(name, None)][prop_name]
            record.prop_value = str(prop_value)
            record = record.table_fit(PROJECT_DATA)
        else:
            record = self.get_row_db_object(name, prop_name, str(prop_value))
        success = sp.new_upd_project_data_array([record])
        if success:
            self.table.update_row_obj(name, prop_name, record)
            self.notify_project_data_changed(self._project_id(), {name})

    def update_column_prop(self, name, prop_name, prop_value):
        if prop_name in self.table.columns[(None, name)]:
            record = self.table.columns[(None, name)][prop_name]
            record.prop_value = str(prop_value)
            record = record.table_fit(PROJECT_DATA)
        else:
            record = self.get_column_db_object(name, prop_name, str(prop_value))
        success = sp.new_upd_project_data_array([record])
        if success:
            self.table.update_column_obj(name, prop_name, record)
            self.notify_project_data_changed(self._project_id(), None)

    def edit_formula_list(self):
        dialog = ManageUserFormulasDialog(self, self.mw)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()


class ProjectPlotPage(PlotPage):
    def __init__(self, item, parent=None, main_window=None):
        super().__init__(item, parent, main_window)
        x_param = str(getattr(item, 'graph_label_x', '') or '').strip()
        y_param = str(getattr(item, 'graph_label_y', '') or '').strip()
        if not x_param or not y_param:
            logger.warning('Graph opened without axis params: graph_id=%s', getattr(getattr(item, '_data', None), 'id', None))
            QMessageBox.warning(self, 'Некорректный график', 'У графика не заданы параметры X/Y.')

        # Определяем действия тулбара в виде словаря
        toolbar_actions = {
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

    def plane_settings(self):
        dialog = EditPlaneDialog(self.item)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()
            if dialog.axis_params_changed:
                self.plotView.reload_data_processor()
            parent_tab = self.parent()
            if parent_tab is not None:
                parent_tab.setWindowTitle(self.item.data())
                index = getattr(parent_tab, 'index', None)
                if index is not None and index.isValid():
                    index.model().dataChanged.emit(index, index)
            self.plotView.refresh()

    def clear_param_cache(self):
        clear_project_param_cache(resolve_project_param_cache_project_id(item=self.item))

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
