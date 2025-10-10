from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

from app.plugins.base_state.models import Node, TreeModel


@dataclass
class SettingsDefinition:
    """Описание узла дерева настроек."""

    identifier: int
    parent_id: int
    title: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SettingsTreeRecord:
    """Представление узла дерева в формате, понятном базовой модели."""

    id: int
    id_up: int
    type_: str
    prop_name: str
    prop_value: Any


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

    def build_from_definitions(self, definitions: Sequence[SettingsDefinition]) -> None:
        """Формирует дерево на основе локального описания."""

        records: List[SettingsTreeRecord] = []

        def _append_record(record_id: int, parent_id: int, name: str, value: Any) -> None:
            records.append(
                SettingsTreeRecord(
                    id=record_id,
                    id_up=parent_id,
                    type_='settings_item',
                    prop_name=name,
                    prop_value=value,
                )
            )

        for definition in definitions:
            base_properties: Dict[str, Any] = {'name': definition.title}
            base_properties.update(definition.properties)

            for prop_name, prop_value in base_properties.items():
                parent = definition.parent_id if prop_name == 'name' else definition.identifier
                _append_record(definition.identifier, parent, prop_name, prop_value)

        self._prop_dict.clear()
        self.ini_tree(records, display_prop='name')
