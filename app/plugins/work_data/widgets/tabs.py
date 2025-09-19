from PySide2.QtCore import QDir, QStandardPaths, QUrl
from PySide2.QtGui import QDesktopServices, Qt
from PySide2.QtWidgets import QLabel

from app.basic_funcs import timing_decorator
from app.plugins.base_state.widgets import Tab
from app.plugins.project.widgets.pages import ProjectPlotPage
from app.plugins.work_data.widgets.pages import WorkDataTablePage1
from db import sp
from db.schemas import ImportFileData
from db.tables import IMPORT_FILE_DATA


class WorkDataTab(Tab):
    @timing_decorator
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        dc = main_window.data_cache
        datafile = sp.get_product_uniskad_files(self.item._data.id, 'input_excel')
        if not datafile:
            main_window.show_notification('Данные для открытия таблицы отсутствуют.')
            return
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
        # Создаем словарь для быстрого доступа к sprav_names по id_name
        sprav_names_dict = {sn.id_name: sn for sn in sprav_names}

        # Создаем словарь для sprav_eizm по id_eizm
        sprav_eizm_dict = {se.id_eizm: se for se in sprav_eizm}

        # Обработка данных
        processed_data = []
        for cell in cells:
            # Данные из sprav_names
            main_sprav = sprav_names_dict.get(cell.id_name)
            perm_sprav = sprav_names_dict.get(main_sprav.id_permanent_name) if main_sprav else None

            # is_secret = perm_sprav.is_secret if perm_sprav else (main_sprav.is_secret if main_sprav else False)
            #
            # if is_secret is not secret_grantness_level:
            #     continue

            # Выбираем данные для param_name, accuracy, param_id_eizm
            sprav_name = perm_sprav.param_name if perm_sprav else (main_sprav.param_name if main_sprav else None)
            accuracy = perm_sprav.accuracy if perm_sprav else (main_sprav.accuracy if main_sprav else None)
            is_secret = perm_sprav.is_secret if perm_sprav else (main_sprav.is_secret if main_sprav else None)
            param_id_eizm = perm_sprav.param_id_eizm if perm_sprav else (
                main_sprav.param_id_eizm if main_sprav else None)

            # Данные из sprav_eizm
            eizm = sprav_eizm_dict.get(param_id_eizm)
            eizm_short = eizm.eizm_short if eizm else None
            eizm_full = eizm.eizm_full if eizm else None

            processed_data.append(ImportFileData({
                'id_excel_file': cell.id_excel_file,
                "id_record": cell.id_record,
                "file_version": cell.file_version,
                'is_secret': is_secret,
                "excel_param_name": sprav_name,
                "param_prop_name": cell.param_prop_name,
                "date_time_izm": cell.date_time_izm,
                "prop_value": cell.prop_value,
                "deleted": cell.deleted,
                "npp": cell.npp,
                "id_name": cell.id_name,
                "sprav_name": sprav_name,
                "accuracy": accuracy,
                "id_eizm": param_id_eizm,
                "eizm_short": eizm_short,
                "eizm_full": eizm_full
            }))

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
