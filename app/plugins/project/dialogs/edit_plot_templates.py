import json

from PySide6.QtWidgets import QTreeWidgetItem

from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_plot_templates import Ui_EditPlotTemplatesDialog
import pyqtgraph as pg

pg.setConfigOptions(background='w', foreground='k', antialias=True)


class EditPlotTemplatesDialog(BaseDialog):

    def __init__(self, graph_folder, plot_templates, parent=None, flags=None):
        super().__init__(parent, flags)
        self.graph_folder = graph_folder
        self.ui = Ui_EditPlotTemplatesDialog()
        self.ui.setupUi(self)

        self.init_trees(plot_templates)
        self.create_connections()

    def create_connections(self):
        self.ui.namesTreeWidget.itemClicked.connect(self.tree_item_clicked)
        self.ui.choosePushButton.clicked.connect(self.accept)
        self.ui.deletePushButton.clicked.connect(self.delete)

    def init_trees(self, plot_templates):
        for t in plot_templates:
            t.value = json.loads(t.value)
            item = QTreeWidgetItem(self.ui.namesTreeWidget)
            item.item_data = t
            item.setText(0, t.value['name'])
            self.ui.namesTreeWidget.addTopLevelItem(item)
        self.ui.namesTreeWidget.headerItem().setText(0, 'Шаблоны')
        self.ui.plainTextEdit.setReadOnly(True)

    def tree_item_clicked(self, item):
        self.ui.plainTextEdit.clear()
        graph_list = item.item_data.value['axis']
        for g in graph_list:
            self.ui.plainTextEdit.appendPlainText(f'{g["y_curve"]} от {g["x_curve"]}')

    def delete(self):
        item = self.ui.namesTreeWidget.selectedItems()[0]
        success = sp.delete_plot_template(item.item_data.id)
        if success:
            self.ui.namesTreeWidget.takeTopLevelItem(self.ui.namesTreeWidget.indexOfTopLevelItem(item))
            self.ui.plainTextEdit.clear()

    def accept(self):
        item = self.ui.namesTreeWidget.selectedItems()[0]
        graphs = sp.add_new_xy_graphs_from_template(self.graph_folder._data.project_id, item.item_data.record_id)
        self.res = graphs
        super().accept()
