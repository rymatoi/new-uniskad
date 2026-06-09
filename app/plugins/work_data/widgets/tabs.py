import time

from PySide2.QtCore import QDir, QStandardPaths, QUrl
from PySide2.QtGui import QDesktopServices, Qt
from PySide2.QtWidgets import QLabel

from app import app_logger
from app.basic_funcs import timing_decorator
from app.plugins.base_state.widgets import Tab
from app.plugins.project.widgets.pages import ProjectPlotPage
from app.plugins.work_data.widgets.pages import WorkDataTablePage1
from db import sp
from db.schemas import ImportFileData
from db.tables import IMPORT_FILE_DATA

logger = app_logger.get_logger(__name__)


class WorkDataTab(Tab):
    @timing_decorator
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        dc = main_window.data_cache
        datafile = sp.get_product_uniskad_files(self.item._data.id, 'input_excel')
        if not datafile:
            main_window.show_notification('Данные для открытия таблицы отсутствуют.')
            return

        logger.debug(
            "Loading work data for id_datafile=%s, file_version=%s",
            datafile.id_datafile,
            int(self.item.final_version),
        )

        cells = sp.get_import_file_data_simple(datafile.id_datafile, int(self.item.final_version))
        sprav_names = dc.get_sprav_names()
        sprav_eizm = dc.get_sprav_eizm()

        is_secret = sp.get_session_role_secret_grantness()

        cells = self.process_data(cells, sprav_names, sprav_eizm, not is_secret)
        cells.sort(
            key=lambda x: (x.id_record, x.excel_param_name, x.param_prop_name, x.date_time_izm))

        self.table_page = WorkDataTablePage1(cells, self.item, self, main_window)
        self.setWidget(self.table_page)

    @timing_decorator
    def process_data(self, cells, sprav_names, sprav_eizm, secret_grantness_level):
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
        columns = (
            'id_excel_file', 'id_record', 'file_version', 'is_secret',
            'excel_param_name', 'param_prop_name', 'date_time_izm',
            'prop_value', 'deleted', 'npp', 'id_name', 'sprav_name',
            'accuracy', 'id_eizm', 'eizm_short', 'eizm_full',
        )
        construct = ImportFileData._get_row_constructor(columns)
        enrichment_get = mapped_enrichment_by_id.get
        empty_mapped_enrichment = empty_enrichment + empty_eizm
        processed_data = []
        append = processed_data.append
        for cell in filtered_cells:
            sprav_name, accuracy, is_secret, id_eizm, eizm_short, eizm_full = enrichment_get(
                cell.id_name, empty_mapped_enrichment)
            append(construct((
                cell.id_excel_file,
                cell.id_record,
                cell.file_version,
                is_secret,
                sprav_name,
                cell.param_prop_name,
                cell.date_time_izm,
                cell.prop_value,
                cell.deleted,
                cell.npp,
                cell.id_name,
                sprav_name,
                accuracy,
                id_eizm,
                eizm_short,
                eizm_full,
            )))
        logger.debug(
            "WorkDataTab.process_data: constructed final list in %.4f seconds "
            "(%d rows)",
            time.perf_counter() - stage_started,
            len(processed_data),
        )
        return processed_data

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
        self.plot_page = ProjectPlotPage(self.item, self)
        self.setWidget(self.plot_page)

    def refresh(self, index):
        """
        Обновление вкладки
        :param index:
        :return:
        """
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
