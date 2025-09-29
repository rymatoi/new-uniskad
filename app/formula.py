import re
from functools import cached_property

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QStandardItemModel, QFont, QStandardItem, Qt
from PySide2.QtWidgets import QCompleter, QStyledItemDelegate


class FormulaDelegate(QStyledItemDelegate):
    def __init__(self, params=None, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.params = params
        self.funcs = [
            'СУММ()',
            'СРЗНАЧ()',
            'МИН()',
            'МАКС()',
            'СЧЁТ()',
            'ЕСЛИ()'
        ]

    def createEditor(self, parent, option, index):
        editor = FormulaLineEdit(params=self._parent.table.ord_rows, funcs=self.funcs, parent=parent)
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.EditRole)
        editor.setText(text)

    def setModelData(self, editor, model, index):
        text = editor.text()
        model.setData(index, text, Qt.EditRole)


class FormulaLineEdit(QtWidgets.QLineEdit):
    """Поле ввода формул с современным автодополнением и вставкой ссылок."""

    text_edited = QtCore.Signal(str)

    def __init__(self, params=None, funcs=None, parent=None):
        super().__init__(parent)

        self.params = params or []
        self.funcs = funcs or []
        self._known_words = set()

        self.setClearButtonEnabled(True)

        self.completer.setWidget(self)
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchContains)

        self.textChanged.connect(self.handle_text_changed)
        self.textChanged.connect(self.text_edited)
        self.completer.activated.connect(self.handle_activated)

        self.set_context(self.params, self.funcs)

    @cached_property
    def model(self):
        return QStandardItemModel()

    @cached_property
    def completer(self):
        return QCompleter()

    def clear_context(self):
        self._known_words.clear()
        self.model.clear()

    def set_context(self, params=None, funcs=None):
        if params is not None:
            self.params = list(params)
        if funcs is not None:
            self.funcs = list(funcs)

        self.clear_context()
        for word in self.funcs + self.params:
            self.add_word(word)

    def add_word(self, word):
        """Добавляет слово в подсказки, избегая дубликатов."""
        if not word:
            return
        if word in self._known_words:
            return
        self._known_words.add(word)
        self.model.appendRow(QStandardItem(word))

    def add_param(self, word):
        """Совместимость: проксирует к :meth:`add_word`."""
        self.add_word(word)

    def handle_text_changed(self):
        text = self.text()[0: self.cursorPosition()]
        if not text:
            self.completer.popup().hide()
            return
        words = text.split()
        if len(words) == 0:
            return
        complete_this = words[-1]
        if complete_this.startswith('"'):
            complete_this = complete_this[1:]

        self.completer.setCompletionPrefix(complete_this)
        if self.completer.completionCount():
            self.completer.complete()

    def handle_activated(self, text):
        prefix = self.completer.completionPrefix()
        extra = text[len(prefix):]
        self.blockSignals(True)
        if extra in self.funcs:
            self.insert(extra)
            self.setCursorPosition(self.cursorPosition() - 1)
        else:
            self.insert(f'{extra}[]"')
            self.setCursorPosition(self.cursorPosition() - 2)

        self.blockSignals(False)

    def insert_reference(self, reference):
        if not reference:
            return
        cursor_position = self.cursorPosition()
        if not self.text().startswith('='):
            self.setText('=' + self.text())
            cursor_position += 1
        self.insert(reference)
        self.setCursorPosition(cursor_position + len(reference))
