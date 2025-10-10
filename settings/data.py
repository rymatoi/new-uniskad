from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class LocalSettingsItem:
    """Простая структура для описания узла настроек."""

    id: int
    id_up: int
    prop_name: str
    prop_value: object
    type_: str = 'settings_item'


def _make_item(node_id: int, parent_id: int, name: str, tab_key: str) -> Iterable[LocalSettingsItem]:
    yield LocalSettingsItem(id=node_id, id_up=parent_id, prop_name='name', prop_value=name)
    yield LocalSettingsItem(id=node_id, id_up=parent_id, prop_name='tab', prop_value=tab_key)


def get_settings_tree() -> List[LocalSettingsItem]:
    """Возвращает локальное дерево настроек."""

    items: List[LocalSettingsItem] = []

    items.extend(_make_item(1, 0, 'Внешний вид', 'appearance'))
    items.extend(_make_item(2, 0, 'Основные', 'general'))

    return items

