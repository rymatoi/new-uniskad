from PySide6.QtCore import QUrl, QStandardPaths, QDir
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel
from app.plugins.base_state.widgets import Tab
from app.plugins.project.widgets.pages import ProjectPlotPage, ProjectTablePage1
from db import sp


class TestTableTab(Tab):
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        item = index.internalPointer()
        cells = sp.get_project_data(self.item._data.project_id)
        a = ProjectTablePage1(cells, item, self, main_window)
        self.setWidget(a)

    def refresh(self, index) -> None:
        cells = sp.get_project_data(self.item._data.project_id)
        self.widget().init_table(cells)
        # self.widget().table.update_table()
        # self.widget().table.load_table(cells)


class GraphTab(Tab):
    """
    Вкладка для отображения графика.
    """

    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self.plot_page = ProjectPlotPage(self.item, self, main_window)
        self.setWidget(self.plot_page)

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        self.plot_page.closeEvent(event)

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
        datafile = sp.get_project_uniskad_files(self.item._data.id, 'other')
        self.binary = sp.get_uniskad_bin_file(datafile.id_datafile)

        filepath = self.download_file()
        QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

    def download_file(self):
        download_folder = QDir(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        filepath = download_folder.filePath(self.item.data())

        with open(filepath, "wb") as file:
            file.write(self.binary.bindata)

        return filepath
