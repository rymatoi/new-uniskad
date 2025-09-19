from app.plugins.base_state.models import Node, TreeModel


class SettingsRoot(Node):
    """Корень дерева первичных данных"""

    @staticmethod
    def internal_type():
        return 'root'

    def columnCount(self):
        return 1

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [SettingsNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def data(self, column=0):
        """То, что отображается в названии узла"""
        return self._data.prop_value


class SettingsNode(SettingsRoot):
    @staticmethod
    def internal_type():
        return 'settings_item'

    def columnCount(self):
        return 1

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []


class SettingsTreeModel(TreeModel):
    """Дерево справочника изделий"""

    def __init__(self):
        super().__init__()
        self._root = SettingsRoot(None)  # переопределяем корень
        self.root_id = 0
        # связать тип элемента с классом в программе
        self.register_nodes(
            [SettingsRoot, SettingsNode])
