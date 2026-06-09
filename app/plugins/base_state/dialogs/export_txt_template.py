import os.path

from PySide6.QtCore import QDir, QItemSelection, QItemSelectionModel
from PySide6.QtWidgets import QAbstractItemView, QDialogButtonBox, QMessageBox, QFileDialog

from app import basic_funcs
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_export_txt_template import Ui_ExportTxtDialog
from resources.ui.ui_py.ui_row_settings import Ui_RowSettingsDialog
from app.utils.encoding import detect_encoding


class Column:
    def __init__(self, i):
        self.i = i
        self.replacement_dict = {}


class ExportTxtDialog(BaseDialog):
    """Диалог выбора файлов для экспорта по шаблону в Txt."""

    def __init__(self, table, parent=None, flags=None):
        super().__init__(parent, flags)

        self.ui = Ui_ExportTxtDialog()
        self.ui.setupUi(self)  # Выставляем UI файл для класса

        self.table = table

        self.columns = {}
        self.parameters = []
        self.dependency_graph = []
        self.order = []
        self.out_template_name = ''

        self.ui.templateName.setText('Шаблон')

        self.convert_button.setText("Экспорт")
        self.cancel_button.setText("Отмена")

        self.convert_button.setEnabled(False)
        self.fill_parameters()
        self.create_connections()

    def search_parameters(self):
        search_text = self.ui.searchLineEdit.text().strip()
        if not search_text:
            # Если строка поиска пуста, показываем все параметры
            self.ui.paramListWidget.clear()
            self.ui.paramListWidget.addItems(self.parameters)
            return

        # Фильтруем параметры по введенному тексту
        filtered_parameters = [param for param in self.parameters if search_text.lower() in param.lower()]

        # Отображаем отфильтрованные параметры
        self.ui.paramListWidget.clear()
        self.ui.paramListWidget.addItems(filtered_parameters)

    def fill_parameters(self):
        self.parameters = [str(val) for val in self.table.ord_rows]
        self.ui.paramListWidget.addItems(self.parameters)

        params = self.table.ord_rows
        self.dependency_graph = {param: [] for param in params}
        for key in params:
            for param in params:
                if param != key and param in key:
                    self.dependency_graph[key].append(param)

        self.order = self.topological_sort(self.dependency_graph)

    def create_connections(self):
        self.ui.loadPushButton.clicked.connect(self.select_template_file)
        self.ui.selectButton.clicked.connect(self.select_dest_file)
        self.cancel_button.clicked.connect(self.close)
        self.convert_button.clicked.connect(self.convert_files)
        self.ui.replaceButton.clicked.connect(self.replace_text)
        self.ui.savePushButton.clicked.connect(self.save_template)
        self.ui.searchLineEdit.textChanged.connect(self.search_parameters)

    def save_template(self):
        txt_file, _ = QFileDialog.getSaveFileName(
            parent=self, caption="Сохранить шаблон",
            directory=QDir.homePath(),
            filter="Txt-file (*.txt)",
        )
        f = open(txt_file, 'w')
        f.write(self.ui.templatePlainText.toPlainText())
        f.close()

    @property
    def convert_button(self) -> "QPushButton":
        """Кнопка для конвертации"""
        return self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)

    @property
    def cancel_button(self) -> "QPushButton":
        """Кнопка для отмены"""
        return self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)

    def replace_text(self):
        selected_item = self.ui.paramListWidget.currentItem()
        if selected_item is None:
            return

        selected_text = selected_item.text()
        cursor = self.ui.templatePlainText.textCursor()
        text_to_replace = cursor.selectedText()

        if text_to_replace == '':
            return

        # Replace the selected text with the new text
        cursor.insertText(selected_text)

        # Set the modified cursor back to the text edit
        self.ui.templatePlainText.setTextCursor(cursor)

    def prepare_export_columns(self):
        line = self.ui.templatePlainText.toPlainText()

        for index in self.table.selectedIndexes():
            item = self.table.itemFromIndex(index)
            self.columns[item.column()] = Column(item.column())

        for i, row in enumerate(self.table.ord_rows):
            for j in self.columns:
                item = self.table.item(i, j)
                self.columns[j].replacement_dict[row] = item.get('cformula', float, item.get('value', float, 0))

    def convert_files(self):
        """Конвертация по шаблону"""
        self.out_template_name = self.ui.exportPathLineEdit.text()
        if os.path.exists(self.out_template_name):
            for column in self.columns:
                template_text = self.process_template(column)
                f = open(self.out_template_name + '/' + f'{self.ui.templateName.text()}_{column}.txt', 'w')
                f.write(template_text)
                f.close()
            self.accept()

    def topological_sort(self, graph):
        visited = set()
        stack = []

        def dfs(node):
            if node not in visited:
                visited.add(node)
                for neighbor in graph.get(node, []):
                    dfs(neighbor)
                stack.append(node)

        for node in graph:
            dfs(node)

        return stack[::-1]

    def process_template(self, column):
        c = self.columns[column]
        template_text = self.ui.templatePlainText.toPlainText()
        # Замена параметров
        for param in self.order:
            template_text = template_text.replace(param, str(c.replacement_dict[param]))
        return template_text

    def select_template_file(self):
        """Открывает окно для выбора шаблона"""
        txt_file, filters = QFileDialog.getOpenFileNames(
            parent=self, caption="Выберите TXT-файл",
            directory=QDir.homePath(),
            filter="Txt-file (*.txt)",

        )
        if txt_file:
            encoding = detect_encoding(txt_file[0])
            if encoding:
                with open(txt_file[0], 'r', encoding=encoding) as f:
                    text = f.read()
                    self.ui.templatePlainText.setPlainText(text)

                self.prepare_export_columns()
            else:
                basic_funcs.error('Не удалось открыть файл',
                                  'Не удалось определить кодировку файла.')

        self.sources_validation()

    def select_dest_file(self):
        """Открывает окно для выбора экспортируемого файла"""
        txt_file = QFileDialog.getExistingDirectory(
            parent=self, caption="Папка для экспорта",
            directory=QDir.homePath()
        )
        self.ui.exportPathLineEdit.setText(txt_file)

        self.sources_validation()

    def sources_validation(self):
        """Если оба - и шаблон и конечный файл - выбраны, то кнопка конвертации становится активной"""
        dest_exists = bool(self.ui.exportPathLineEdit.text())
        name_exists = bool(self.ui.templateName.text())
        self.convert_button.setEnabled(dest_exists and name_exists)
