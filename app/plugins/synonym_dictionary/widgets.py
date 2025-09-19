from copy import copy

from PySide2.QtCore import QModelIndex

from app.basic_funcs import error
from app.plugins.base_state.widgets import TreeView, Tab
from app.plugins.eizm_dictionary.models import EizmDictionaryTreeModel
from app.plugins.eizm_dictionary.widgets import EizmDictionaryTreeView
from app.plugins.synonym_dictionary.dialogs.confirm_parameter import ParameterConfirmDialog
from app.plugins.synonym_dictionary.dialogs.link_eizm import LinkEizmDialog
from app.plugins.synonym_dictionary.models import SynonymNode, StandardNode
from db import sp
from resources.ui.ui_py.ui_parameter_widget import Ui_ParameterWidget


class ParameterTab(Tab):
    def __init__(self, index, parent, main_window=None):
        super().__init__(index, parent, main_window)

        self.setupUi(Ui_ParameterWidget())

        eizm_model = EizmDictionaryTreeModel()
        self.tree_items = sp.get_name_all_eizm(self.item._data.id_name)
        eizm_model.ini_tree(self.tree_items)

        self.ui.treeView_ = EizmDictionaryTreeView(self, main_window=main_window)
        self.ui.treeView_.DOUBLE_CLICK_OPEN = False
        self.ui.treeView_.DISABLE_MENU = True
        self.ui.treeView_.setModel(eizm_model)

        self.ui.gridLayout.replaceWidget(self.ui.treeView, self.ui.treeView_)
        self.ui.treeView.deleteLater()
        self.create_connections()

        self._current_set_eizm_index = None

        self._before()

    def _before(self):
        root = self.ui.treeView_.root_item()
        for item in root._children:
            if self.item._data.param_id_eizm == item._data.id_eizm:
                self._current_set_eizm_index = self.ui.treeView_.model().index(item.row(), 0, QModelIndex())
                self.ui.treeView_.change_property('bold', self._current_set_eizm_index)

        self.ui.checkBox.setChecked(self.item._data.is_secret)

    def create_connections(self):
        self.ui.addButton.clicked.connect(self.link_eizm)
        self.ui.removeButton.clicked.connect(self.unlink_eizm)
        self.ui.selectButton.clicked.connect(self.select_eizm)

    def select_eizm(self):
        selected_index = self.ui.treeView_.selectedIndexes()
        if not selected_index:
            return
        index = selected_index[0]

        self.ui.treeView_.change_property('bold', self._current_set_eizm_index)
        self.ui.treeView_.change_property('bold', index)
        self._current_set_eizm_index = copy(index)

    def link_eizm(self):
        dialog = LinkEizmDialog(self.item, exclude=[item.id_eizm for item in self.tree_items])
        if dialog.exec_():  # Если произошло изменение данных
            success = sp.add_link_name_eizm_array(self.item._data.id_name,
                                                  [item._data.id_eizm for item in dialog.get_result()])
            if success:
                self.tree_items += [node._data for node in dialog.get_result()]
                self.ui.treeView_.insertRows(dialog.get_result(), QModelIndex())
            else:
                error('Ошибка!', "Не удалось добавить отношение.")

    def unlink_eizm(self):
        selected_index = self.ui.treeView_.selectedIndexes()
        if selected_index:
            index = selected_index[0]
            item = index.internalPointer()
            success = sp.remove_link_name_eizm(self.item._data.id_name, item._data.id_eizm)
            if success:
                self.ui.treeView_.removeRow(index.row(), index.parent())
                self.tree_items.remove(item._data)
            else:
                error('Ошибка!', "Не удалось удалить отношение.")

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
        sp.set_param_secret(self.item._data.param_name, self.ui.checkBox.isChecked())
        self.item._data.is_secret = self.ui.checkBox.isChecked()


class SynonymDictionaryTreeView(TreeView):
    def __init__(self, parent, main_window=None):
        super().__init__(parent, main_window)
        self.treeview_menu = self._load_menu('synonym_dictionary', 'synonym_dictionary_treeview')
        self.link_nodes_with_tabs({
            SynonymNode: ParameterTab,
            StandardNode: ParameterTab,
        })

    def connect_triggered_funcs(self, index):
        self._connect_func('_confirm_unknown', self.confirm, index)
        self._connect_func('_unconfirm_synonym', self.unconfirm, index)
        self._connect_func('_unconfirm_standard', self.unconfirm, index)

    def confirm(self, index):
        item = index.internalPointer()
        dialog = ParameterConfirmDialog(item)
        if dialog.exec_():  # Если произошло изменение данных
            self.model().confirm_parameter(dialog.current)
            self.model().remove_parameter(item)

    def unconfirm(self, index):
        item = index.internalPointer()

        sp.set_flag_synonim_sprav_names(item.data(), False, None)
        sp.set_flag_permanent_sprav_names(item.data(), False)

        self.model().unconfirm_parameter(copy(item))
        self.model().remove_parameter(item)
