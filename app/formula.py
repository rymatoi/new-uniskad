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
        self.funcs = ['sin()', 'cos()', 'avg()']

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
    """
    Класс, регулирующий работу LineEdit для написаний формул
    Сейчас контролирует механизм подсказок при наборе (предлагает функции из заданого набора funcs)
    """
    text_edited = QtCore.Signal(str)

    def __init__(self, params, funcs, parent=None):
        super().__init__(parent)

        self.params = params
        self.funcs = funcs

        self.completer.setWidget(self)
        self.completer.setModel(self.model)
        self.textChanged.connect(self.handle_text_changed)
        self.textChanged.connect(self.text_edited)
        self.completer.activated.connect(self.handle_activated)
        for word in self.params + self.funcs:
            self.add_word(word)

    @cached_property
    def model(self):
        return QStandardItemModel()

    @cached_property
    def completer(self):
        return QCompleter()

    def add_word(self, word):
        """
        Добавления слова для подсказки
        """
        if not self.model.findItems(word):
            self.model.appendRow(QStandardItem(word))

    def add_param(self, word):
        """
        Добавления слова для подсказки
        """
        if not self.model.findItems(word):
            self.model.appendRow(QStandardItem(word))

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
