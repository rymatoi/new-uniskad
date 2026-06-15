from time import perf_counter

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QPushButton, QTreeWidgetItem

from app import app_logger
from app.plugins.base_state.widgets import ExtendedComboBox
from app.plugins.project import utils
from app.plugins.project.utils_ import get_project_params, collect_cell_values
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_extra_param_epure import Ui_ExtraParamEoure


logger = app_logger.get_logger(__name__)


class ExtraParamEpureDialog(BaseDialog):

    def __init__(self, test_nodes, project_id, extra_param, extra_param_values, flags=None, *args, **kwargs):
        started = perf_counter()
        super().__init__(flags, *args, **kwargs)
        self.project_id = project_id
        self.test_nodes = test_nodes
        self.ui = Ui_ExtraParamEoure()
        self.ui.setupUi(self)
        self.selectionButtonsLayout = QHBoxLayout()
        self.selectAllButton = QPushButton('Выбрать все', self)
        self.clearAllButton = QPushButton('Снять все', self)
        self.selectionButtonsLayout.addWidget(self.selectAllButton)
        self.selectionButtonsLayout.addWidget(self.clearAllButton)
        self.ui.verticalLayout.insertLayout(3, self.selectionButtonsLayout)
        self.comboBox = ExtendedComboBox(self)
        self.ui.verticalLayout.replaceWidget(self.ui.comboBox, self.comboBox)
        self.ui.comboBox.deleteLater()
        self.ui.comboBox.hide()
        self.ui.comboBox = None

        self.selected = extra_param_values

        self.param_list = get_project_params(project_id)
        self.param_values_dict = {}
        self.current_param = extra_param
        self.create_connections()  # создаем привязки

        self.ui.treeWidget.setHeaderLabel('')

        self.load_params()
        logger.info(
            "SelectionDialog initialized: class=%s, items=%d, elapsed=%.4fs",
            self.__class__.__name__, self.ui.treeWidget.topLevelItemCount(), perf_counter() - started,
        )

    def create_connections(self):
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.close)
        self.comboBox.currentTextChanged.connect(self.load_param_values)
        self.selectAllButton.clicked.connect(self.select_all)
        self.clearAllButton.clicked.connect(self.clear_all)

    def load_params(self):
        self.comboBox.addItems(['Пусто'] + list(self.param_list.keys()))
        self.comboBox.setCurrentText(self.current_param if self.current_param else 'Пусто')

    def load_param_values(self, text):
        if text == 'Пусто':
            self.fill_tree_widget([])
            self.current_param = None
            return

        if text not in self.param_list:
            return

        self.current_param = text

        if text not in self.param_values_dict:
            z_data = collect_cell_values(
                sp.get_x_curves(self.project_id, [test._data.project_id for test in self.test_nodes],
                                text))
            self.param_values_dict[text] = []
            for val in list(z_data.values()):
                self.param_values_dict[text] += val

        self.fill_tree_widget(set(self.param_values_dict[text]))

    def fill_tree_widget(self, values):
        widget = self.ui.treeWidget
        widget.setUpdatesEnabled(False)
        widget.blockSignals(True)
        try:
            widget.clear()
            for val in values:
                child = QTreeWidgetItem(widget)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setCheckState(0, Qt.Unchecked if val.prop_value not in self.selected else Qt.Checked)
                child.setText(0, val.prop_value)
        finally:
            widget.blockSignals(False)
            widget.setUpdatesEnabled(True)
            widget.viewport().update()

    def select_all(self):
        self._set_all_checked(Qt.Checked, 'select_all')

    def clear_all(self):
        self._set_all_checked(Qt.Unchecked, 'clear_all')

    def _set_all_checked(self, state, action):
        started = perf_counter()
        widget = self.ui.treeWidget
        affected = 0
        widget.setUpdatesEnabled(False)
        widget.blockSignals(True)
        try:
            for row in range(widget.topLevelItemCount()):
                item = widget.topLevelItem(row)
                if not item.flags() & Qt.ItemIsEnabled or not item.flags() & Qt.ItemIsUserCheckable:
                    continue
                item.setCheckState(0, state)
                affected += 1
        finally:
            widget.blockSignals(False)
            widget.setUpdatesEnabled(True)
            widget.viewport().update()
        selected = sum(
            widget.topLevelItem(row).checkState(0) == Qt.Checked
            for row in range(widget.topLevelItemCount())
        )
        logger.info(
            "SelectionDialog %s completed: class=%s, affected=%d, selected=%d, elapsed=%.4fs",
            action, self.__class__.__name__, affected, selected, perf_counter() - started,
        )

    def accept(self) -> None:
        res = []
        root = self.ui.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) is Qt.CheckState.Checked:
                res.append(item.text(0))
        self.res = self.current_param, res
        super().accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
