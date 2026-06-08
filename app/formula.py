import re
from functools import cached_property

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QFont, QStandardItem
from PySide6.QtWidgets import QCompleter, QStyledItemDelegate


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
            'ЕСЛИ(; ; )',
            'ABS()',
            'МОДУЛЬ()',
            'POWER(, )',
            'СТЕПЕНЬ(, )',
            'ROUND(, )',
            'ОКРУГЛ(, )',
            'AND(, )',
            'И(, )',
            'OR(, )',
            'ИЛИ(, )',
            'NOT()',
            'НЕ()',
            'RANGE(; )',
            'ДИАПАЗОН(; )',
            'COLUMN()',
            'СТОЛБЕЦ()'
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
        self._completion_region = None
        self._programmatic_change = False

        self.setClearButtonEnabled(True)

        self.completer.setWidget(self)
        self.completer.setModel(self.model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchContains)

        self.textChanged.connect(self._handle_text_changed)
        self.textEdited.connect(self._handle_text_edited)
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

    def setText(self, text):
        self._programmatic_change = True
        try:
            super().setText(text)
        finally:
            self._programmatic_change = False
        self._completion_region = None
        self.completer.popup().hide()

    def _extract_completion_region(self, text):
        """Возвращает диапазон последней лексемы для автодополнения."""
        if not text:
            return None

        cursor = len(text)
        last_quote = text.rfind('"')
        if last_quote != -1:
            tail = text[last_quote + 1:]
            if '"' not in tail:
                # Если после кавычки уже встретились арифметические операторы или
                # разделители, значит курсор вышел из строкового литерала и нужно
                # искать обычную лексему. В противном случае продолжаем работать
                # как с параметром в кавычках.
                if not re.search(r'[+\-*/=(),;]', tail):
                    return {
                        'start': last_quote + 1,
                        'replace_start': last_quote,
                        'end': cursor,
                        'prefix': tail,
                    }

        match = re.search(r'([A-Za-zА-Яа-яЁё0-9_]+)$', text)
        if not match:
            return None
        return {
            'start': match.start(1),
            'replace_start': match.start(1),
            'end': cursor,
            'prefix': match.group(1),
        }

    def _has_matches(self, prefix):
        if not self._known_words:
            return False
        lowered = prefix.lower()
        return any(lowered in word.lower() for word in self._known_words)

    def _update_completion(self):
        upto_cursor = self.text()[:self.cursorPosition()]
        region = self._extract_completion_region(upto_cursor)
        self._completion_region = region
        if region is None:
            self.completer.popup().hide()
            return

        prefix = region['prefix']
        if not self._has_matches(prefix):
            self.completer.popup().hide()
            return
        self.completer.setCompletionPrefix(prefix)
        self.completer.complete()

    def _handle_text_changed(self, text):
        if self._programmatic_change:
            self.completer.popup().hide()
            self._completion_region = None

    def _handle_text_edited(self, text):
        self.text_edited.emit(text)
        if self._programmatic_change:
            return
        self._update_completion()

    def handle_activated(self, text):
        region = self._completion_region
        if region is None:
            return

        start = region['start']
        replace_start = region['replace_start']
        end = region['end']
        before = self.text()[:start]
        replace_before = self.text()[:replace_start]
        after = self.text()[end:]

        self.blockSignals(True)
        if text in self.funcs:
            replacement = text
            new_text = before + replacement + after
            self.setText(new_text)
            cursor = len(before) + len(replacement)
            if replacement.endswith(')'):
                cursor -= 1
            self.setCursorPosition(cursor)
        else:
            replacement = f'"{text}[]"'
            new_text = replace_before + replacement + after
            self.setText(new_text)
            cursor = len(replace_before) + len(text) + 2
            self.setCursorPosition(cursor)

        self.blockSignals(False)
        self._completion_region = None

    def insert_reference(self, reference):
        if not reference:
            return
        cursor_position = self.cursorPosition()
        if not self.text().startswith('='):
            self.setText('=' + self.text())
            cursor_position += 1
        self.insert(reference)
        self.setCursorPosition(cursor_position + len(reference))
