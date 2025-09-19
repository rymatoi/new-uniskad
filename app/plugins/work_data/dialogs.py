from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

from db import sp
from db.tables import PRODUCT
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_version_control_dialog import Ui_VersionControlDialog


class VersionControlDialog(BaseDialog):

    def __init__(self, item, parent=None, flags=None):
        super().__init__(parent, flags)
        self.ui = Ui_VersionControlDialog()
        self.ui.setupUi(self)
        self.create_connections()  # создаем привязки

        self.item = item
        self.datafile = sp.get_product_uniskad_files(self.item._data.id, 'input_excel')
        self.file_versions = []
        self.init_combobox()

    def init_combobox(self):
        self.ui.versionComboBox.clear()
        file_versions = sp.get_import_file_data_versions(self.datafile.id_datafile)
        self.file_versions = [str(version.file_version) for version in file_versions]
        self.ui.versionComboBox.addItems(self.file_versions)
        self.ui.versionComboBox.setCurrentText(self.item.final_version)

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.removeButton.clicked.connect(self.remove)
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.newButton.clicked.connect(self.new)
        self.ui.versionComboBox.activated[str].connect(self.combo_changed)

    def combo_changed(self, text):
        self.item.final_version = text

    def new(self):
        self.file_versions.append(str(int(max(self.file_versions)) + 1))
        sp.new_import_file_data_version(self.datafile.id_datafile, int(self.item.final_version),
                                        int(self.item.final_version) + 1)
        self.item.final_version = max(self.file_versions)
        self.init_combobox()

    def save(self):
        self.res = self.item.final_version
        self.accept()

    def remove(self):
        if self.ui.versionComboBox.count() == 1:
            pass
        else:
            sp.remove_import_file_data_version(self.datafile.id_datafile, int(self.ui.versionComboBox.currentText()))
            self.file_versions.remove(self.ui.versionComboBox.currentText())
            self.init_combobox()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
