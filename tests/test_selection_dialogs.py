import os

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide2')

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

from app.plugins.project.dialogs.select_test_data import TestDataSelectionDialog


@pytest.fixture(scope='module')
def application():
    return QApplication.instance() or QApplication([])


def test_test_data_selection_batches_filtered_rows_and_keeps_manual_changes(application):
    dialog = TestDataSelectionDialog(['keep one', 'hide', 'keep two'])

    dialog.search_line_changed('keep')
    dialog.select_all()
    assert [node.name for node in dialog.model.checked_list] == ['keep one', 'keep two']

    dialog.search_line_changed('')
    hidden_index = dialog.model.index(1, 0)
    dialog.model.setData(hidden_index, Qt.Checked, Qt.CheckStateRole)
    assert len(dialog.model.checked_list) == 3

    dialog.search_line_changed('keep')
    dialog.clear_all()
    assert [node.name for node in dialog.model.checked_list] == ['hide']
    assert dialog.ui.selectAllButton.text() == 'Выбрать все'
    assert dialog.ui.clearAllButton.text() == 'Снять все'

    dialog.close()


def test_test_data_selection_does_not_select_disabled_rows(application, monkeypatch):
    dialog = TestDataSelectionDialog(['enabled', 'disabled'])
    original_flags = dialog.model.flags

    def flags(index):
        result = original_flags(index)
        if index.isValid() and index.row() == 1:
            return result & ~Qt.ItemIsEnabled
        return result

    monkeypatch.setattr(dialog.model, 'flags', flags)
    dialog.select_all()

    assert [node.name for node in dialog.model.checked_list] == ['enabled']
    dialog.close()
