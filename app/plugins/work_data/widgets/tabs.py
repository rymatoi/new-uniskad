import time

from PySide2.QtCore import QDir, QStandardPaths, QUrl
from PySide2.QtGui import QDesktopServices, Qt
from PySide2.QtWidgets import QLabel

from app import app_logger
from app.basic_funcs import timing_decorator
from app.feature_flags import is_feature_enabled
from app.plugins.base_state.widgets import Tab
from app.plugins.project.widgets.pages import ProjectPlotPage
from app.plugins.work_data.widgets.pages import WorkDataTablePage1, WorkDataTableViewPage
from db import sp
from db.tables import IMPORT_FILE_DATA

logger = app_logger.get_logger(__name__)


class WorkDataTab(Tab):
    @timing_decorator
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self._loaded = False
        self._loading = False
        self._refresh_pending = False
        self.table_page = None
        self._placeholder = QLabel('Таблица будет загружена при открытии.', self)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self.setWidget(self._placeholder)
        self.visibilityChanged.connect(self._load_when_visible)
        logger.info(
            "WorkData table tab registered as placeholder: product_id=%s, title=%s",
            getattr(self.item._data, 'id', None),
            self.windowTitle(),
        )

    def _load_when_visible(self, visible):
        if visible and not getattr(self._parent, '_restoring_tabs', False):
            self.ensure_loaded()

    def _load_cells(self):
        dc = self.main_window.data_cache
        datafile = sp.get_product_uniskad_files(self.item._data.id, 'input_excel')
        if not datafile:
            self.main_window.show_notification('Данные для открытия таблицы отсутствуют.')
            return None

        logger.debug(
            "Loading work data for id_datafile=%s, file_version=%s",
            datafile.id_datafile,
            int(self.item.final_version),
        )

        db_started = time.perf_counter()
        cells = sp.get_import_file_data_simple(datafile.id_datafile, int(self.item.final_version))
        sprav_names = dc.get_sprav_names()
        sprav_eizm = dc.get_sprav_eizm()
        logger.info('WorkDataTab: DB/cache fetch took %.4f seconds', time.perf_counter() - db_started)

        is_secret = sp.get_session_role_secret_grantness()

        enrichment_started = time.perf_counter()
        cells = self.process_data(cells, sprav_names, sprav_eizm, not is_secret)
        logger.info('WorkDataTab: enrichment took %.4f seconds', time.perf_counter() - enrichment_started)
        cells.sort(
            key=lambda x: (x.id_record, x.excel_param_name, x.param_prop_name, x.date_time_izm))
        return cells

    def ensure_loaded(self):
        if self._loaded:
            logger.info(
                "WorkData table page load reused from cache: product_id=%s, title=%s",
                getattr(self.item._data, 'id', None),
                self.windowTitle(),
            )
            return self.widget()
        if self._loading:
            return self.widget()

        self._loading = True
        logger.info(
            "WorkData table page first load: product_id=%s, title=%s",
            getattr(self.item._data, 'id', None),
            self.windowTitle(),
        )
        try:
            cells = self._load_cells()
            if cells is None:
                return self.widget()
            use_table_view = is_feature_enabled('UNISKAD_WORK_DATA_TABLE_VIEW', default=True)
            page_class = WorkDataTableViewPage if use_table_view else WorkDataTablePage1
            logger.info("Work Data table implementation: %s", page_class.__name__)
            self.table_page = page_class(cells, self.item, self, self.main_window)
            self.setWidget(self.table_page)
            self._loaded = True
            self._refresh_pending = False
            return self.table_page
        finally:
            self._loading = False

    def refresh(self, index):
        if not self._loaded:
            self._refresh_pending = True
            logger.debug(
                "WorkData table refresh deferred until first load: product_id=%s",
                getattr(self.item._data, 'id', None),
            )
            return
        cells = self._load_cells()
        if cells is None:
            return
        if self.table_page is not None:
            self.table_page.init_table(cells)

    @timing_decorator
    def process_data(self, cells, sprav_names, sprav_eizm, secret_grantness_level):
        total_started = time.perf_counter()
        stage_started = time.perf_counter()
        sprav_names_by_id = {item.id_name: item for item in sprav_names}
        sprav_eizm_by_id = {item.id_eizm: item for item in sprav_eizm}
        logger.debug(
            "WorkDataTab.process_data: built lookup dictionaries in %.4f seconds "
            "(%d names, %d units)",
            time.perf_counter() - stage_started,
            len(sprav_names_by_id),
            len(sprav_eizm_by_id),
        )

        stage_started = time.perf_counter()
        # Secret filtering is intentionally a pass-through here, matching the
        # existing behavior.  The flag is still logged so this stage can be
        # measured and filtering can be restored separately if required.
        filtered_cells = cells
        logger.debug(
            "WorkDataTab.process_data: filtered secret rows in %.4f seconds "
            "(pass-through, secret_grantness_level=%s, %d rows)",
            time.perf_counter() - stage_started,
            secret_grantness_level,
            len(filtered_cells),
        )

        stage_started = time.perf_counter()
        empty_enrichment = (None, None, None, None)
        enrichment_by_id = {}
        names_get = sprav_names_by_id.get
        for id_name, main_sprav in sprav_names_by_id.items():
            perm_sprav = names_get(main_sprav.id_permanent_name)
            resolved_sprav = perm_sprav if perm_sprav is not None else main_sprav
            enrichment_by_id[id_name] = (
                resolved_sprav.param_name,
                resolved_sprav.accuracy,
                resolved_sprav.is_secret,
                resolved_sprav.param_id_eizm,
            )
        logger.debug(
            "WorkDataTab.process_data: enriched sprav_names in %.4f seconds "
            "(%d resolved names)",
            time.perf_counter() - stage_started,
            len(enrichment_by_id),
        )

        stage_started = time.perf_counter()
        eizm_values_by_id = {
            id_eizm: (eizm.eizm_short, eizm.eizm_full)
            for id_eizm, eizm in sprav_eizm_by_id.items()
        }
        empty_eizm = (None, None)
        eizm_get = eizm_values_by_id.get
        mapped_enrichment_by_id = {
            id_name: enrichment + eizm_get(enrichment[3], empty_eizm)
            for id_name, enrichment in enrichment_by_id.items()
        }
        logger.debug(
            "WorkDataTab.process_data: mapped units/eizm in %.4f seconds "
            "(%d mapped names)",
            time.perf_counter() - stage_started,
            len(mapped_enrichment_by_id),
        )

        stage_started = time.perf_counter()
        enrichment_get = mapped_enrichment_by_id.get
        empty_mapped_enrichment = empty_enrichment + empty_eizm
        for cell in filtered_cells:
            sprav_name, accuracy, is_secret, id_eizm, eizm_short, eizm_full = enrichment_get(
                cell.id_name, empty_mapped_enrichment)
            cell.is_secret = is_secret
            cell.excel_param_name = sprav_name
            cell.sprav_name = sprav_name
            # Keep both sides of the QueryField alias synchronized when rows
            # came from either the optimized or legacy DB parser.
            cell.prop_name = cell.param_prop_name
            cell.accuracy = accuracy
            cell.id_eizm = id_eizm
            cell.eizm_short = eizm_short
            cell.eizm_full = eizm_full
        logger.debug(
            "WorkDataTab.process_data: enriched rows in place in %.4f seconds "
            "(%d rows)",
            time.perf_counter() - stage_started,
            len(filtered_cells),
        )
        logger.debug(
            "WorkDataTab.process_data: total in-place processing took %.4f seconds",
            time.perf_counter() - total_started,
        )
        return filtered_cells

    def add_data(self, obj_list):
        if not obj_list:
            return
        max_row = len(self.model.cell_table.rows)
        max_column = len(self.model.cell_table.columns)
        obj_list = sp.import_file_data_w_joins([obj.table_fit(IMPORT_FILE_DATA) for obj in obj_list])
        self.model.cell_table.add_data(obj_list)
        self.model.insertRows(max_row, len(self.model.cell_table.rows) - max_row)
        self.model.insertColumns(max_column, len(self.model.cell_table.columns) - max_column)


class GraphTab(Tab):
    """
    Вкладка для отображения графика.
    """

    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self._loaded = False
        self._loading = False
        self._refresh_pending = False
        self.plot_page = None
        self._placeholder = QLabel('График будет загружен при открытии.', self)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self.setWidget(self._placeholder)
        self.visibilityChanged.connect(self._load_when_visible)
        logger.info(
            "Project graph tab registered as placeholder: node_id=%s, title=%s",
            getattr(self.item._data, 'id', None),
            self.windowTitle(),
        )

    def _load_when_visible(self, visible):
        if visible and not getattr(self._parent, '_restoring_tabs', False):
            self.ensure_loaded()

    def ensure_loaded(self):
        if self._loaded:
            return self.widget()
        if self._loading:
            return self.widget()

        self._loading = True
        logger.info(
            "Project graph page first load: node_id=%s, title=%s",
            getattr(self.item._data, 'id', None),
            self.windowTitle(),
        )
        try:
            self.plot_page = ProjectPlotPage(self.item, self)
            self.setWidget(self.plot_page)
            self._loaded = True
            self._refresh_pending = False
            return self.plot_page
        finally:
            self._loading = False

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        if self.plot_page is not None:
            self.plot_page.closeEvent(event)

    def refresh(self, index):
        """
        Обновление вкладки
        :param index:
        :return:
        """
        if not self._loaded:
            self._refresh_pending = True
            logger.debug(
                "Project graph refresh deferred until first load: node_id=%s",
                getattr(self.item._data, 'id', None),
            )
            return
        self.setWindowTitle(self.item.data())
        plot_view = getattr(self.plot_page, 'plotView', None)
        if plot_view is not None and getattr(self.item, 'internal_type', lambda: None)() == 'graph':
            plot_view.reload_data_processor()
        self.plot_page.refresh(index)


class FileTab(Tab):

    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self.label = QLabel('Файл открыт в стороннем приложении.')
        self.label.setAlignment(Qt.AlignCenter)
        self.setWidget(self.label)
        self.open_file()

    def open_file(self):
        datafile = sp.get_product_uniskad_files(self.item._data.id, 'other')
        self.binary = sp.get_uniskad_bin_file(datafile.id_datafile)
        filepath = self.download_file()
        QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

    def download_file(self):
        download_folder = QDir(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        filepath = download_folder.filePath(self.item.data())

        with open(filepath, "wb") as file:
            file.write(self.binary.bindata)

        return filepath
