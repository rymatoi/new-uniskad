import re
from functools import cached_property

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QStandardItemModel, QFont, QStandardItem, Qt
from PySide2.QtWidgets import QCompleter, QStyledItemDelegate


class FormulaDelegate(QStyledItemDelegate):
    def __init__(self, params=None, columns=None, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.params = params or []
        self.columns = columns or []
        self.funcs = [
            'SUM()', 'AVERAGE()', 'MIN()', 'MAX()', 'IF()', 'ROUND()', 'SIN()', 'COS()'
        ]

    def createEditor(self, parent, option, index):
        editor = FormulaLineEdit(
            params=self._parent.table.ord_rows,
            columns=self._parent.table.ord_columns,
            funcs=self.funcs,
            parent=parent
        )
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.EditRole)
        editor.setText(text)

    def setModelData(self, editor, model, index):
        text = editor.text()
        model.setData(index, text, Qt.EditRole)


class FormulaLineEdit(QtWidgets.QLineEdit):
    """Поле ввода формулы с автодополнением и подсказками."""

    text_edited = QtCore.Signal(str)

    def __init__(self, params, columns, funcs, parent=None):
        super().__init__(parent)

        self.params = params or []
        self.columns = columns or []
        self.funcs = funcs or []
        self.completion_kinds = {}

        self.setPlaceholderText('Введите формулу, например =SUM(A1,B1)')
        self.setClearButtonEnabled(True)

        self.completer.setWidget(self)
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        self.textChanged.connect(self.handle_text_changed)
        self.textChanged.connect(self.text_edited)
        self.completer.activated.connect(self.handle_activated)

        self._populate_completions()

    @cached_property
    def model(self):
        return QStandardItemModel()

    @cached_property
    def completer(self):
        return QCompleter()

    def _populate_completions(self):
        for func in self.funcs:
            self.add_word(func, kind='function')

        for param in self.params:
            if param:
                self.add_word(param, kind='row')

        max_refs = 2000
        added = 0
        for reference in self._iter_excel_references():
            self.add_word(reference, kind='cell')
            added += 1
            if added >= max_refs:
                break

    def _iter_excel_references(self):
        if not self.columns:
            return
        for column_index in range(len(self.columns)):
            column_name = self._excel_column_name(column_index)
            for row_index in range(len(self.params)):
                yield f'{column_name}{row_index + 1}'

    @staticmethod
    def _excel_column_name(index):
        if index < 0:
            return ''
        name = ''
        while True:
            index, remainder = divmod(index, 26)
            name = chr(ord('A') + remainder) + name
            if index == 0:
                break
            index -= 1
        return name

    def add_word(self, word, kind='literal'):
        """Добавление слова для подсказки."""
        if not word:
            return
        existing = self.model.findItems(word)
        if not existing:
            item = QStandardItem(word)
            item.setData(kind, Qt.UserRole)
            self.model.appendRow(item)
        self.completion_kinds[word] = kind

    def add_param(self, word):
        self.add_word(word, kind='row')

    def handle_text_changed(self):
        text = self.text()[0: self.cursorPosition()]
        if not text:
            self.completer.popup().hide()
            return

        parts = re.split(r'[\s\+\-\*/=,;\(\):]+', text)
        if not parts:
            return

        complete_this = parts[-1]
        if complete_this.startswith('"'):
            complete_this = complete_this[1:]

        if not complete_this:
            self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(complete_this)
        self.completer.complete()

    def handle_activated(self, text):
        prefix = self.completer.completionPrefix()
        kind = self.completion_kinds.get(text, 'literal')
        self.blockSignals(True)

        start = self.cursorPosition() - len(prefix) if prefix else self.cursorPosition()
        if prefix:
            self.setSelection(max(start, 0), len(prefix))

        if kind == 'function':
            self.insert(text)
            if text.endswith('()'):
                self.setCursorPosition(self.cursorPosition() - 1)
        elif kind == 'row':
            escaped = text.replace('"', '\\"')
            replacement = f'"{escaped}"'
            self.insert(replacement)
        else:
            self.insert(text)

        self.blockSignals(False)
