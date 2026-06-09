from time import perf_counter

from PySide2.QtCore import QUrl, QStandardPaths, QDir
from PySide2.QtGui import QDesktopServices, Qt
from PySide2.QtWidgets import QLabel

from app import app_logger
from app.plugins.base_state.widgets import Tab
from app.plugins.project.widgets.pages import ProjectPlotPage, ProjectTablePage1
from db import sp

logger = app_logger.get_logger(__name__)


class TestTableTab(Tab):
    """Project table dock that creates its heavy page on first activation."""

    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)
        self._loaded = False
        self._loading = False
        self._refresh_pending = False
        self._placeholder = QLabel('Таблица будет загружена при открытии.', self)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self.setWidget(self._placeholder)
        self.visibilityChanged.connect(self._load_when_visible)
        logger.info(
            "Project table page registered as placeholder: project_id=%s, title=%s",
            self.item._data.project_id, self.windowTitle(),
        )

    def _load_when_visible(self, visible):
        if visible and not getattr(self._parent, '_restoring_tabs', False):
            self.ensure_loaded()

    def ensure_loaded(self):
        """Create and cache the table page the first time this tab is active."""
        if self._loaded:
            logger.info(
                "Project table page load reused from cache: project_id=%s, title=%s",
                self.item._data.project_id, self.windowTitle(),
            )
            return self.widget()
        if self._loading:
            return self.widget()

        self._loading = True
        started = perf_counter()
        project_id = self.item._data.project_id
        logger.info(
            "Project table page first load: project_id=%s, title=%s",
            project_id, self.windowTitle(),
        )
        try:
            cells = sp.get_project_data(project_id)
            elapsed_ms = (perf_counter() - started) * 1000
            logger.info(
                "Project get_project_data completed: project_id=%s, elapsed_ms=%.1f",
                project_id, elapsed_ms,
            )
            page = ProjectTablePage1(cells, self.item, self, self.main_window)
            self.setWidget(page)
            self._loaded = True
            self._refresh_pending = False
            logger.info(
                "Project table page freshly created: project_id=%s, elapsed_ms=%.1f",
                project_id, (perf_counter() - started) * 1000,
            )
            return page
        finally:
            self._loading = False

    def refresh(self, index) -> None:
        if not self._loaded:
            self._refresh_pending = True
            logger.debug(
                "Project table page refresh deferred until first load: project_id=%s",
                self.item._data.project_id,
            )
            return
        started = perf_counter()
        cells = sp.get_project_data(self.item._data.project_id)
        logger.info(
            "Project get_project_data refresh completed: project_id=%s, elapsed_ms=%.1f",
            self.item._data.project_id, (perf_counter() - started) * 1000,
        )
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
