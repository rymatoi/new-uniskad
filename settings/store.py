"""Local settings tree description used by the settings dialog.

This module contains a small helper that mimics the structure normally
returned by the database and provides a declarative description of the
settings sections that are available in the application.  The data is
represented with the same ``SettingsItem`` objects that the tree model
expects, so the rest of the UI can remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Iterable, List, Optional

from db.schemas import SettingsItem


@dataclass(frozen=True)
class SettingsNodeDescription:
    """Description of a single item in the settings tree."""

    title: str
    children: Optional[Iterable["SettingsNodeDescription"]] = None

    def iter_children(self) -> Iterable["SettingsNodeDescription"]:
        return self.children or []


def _create_item(node_id: int, parent_id: int, title: str) -> SettingsItem:
    """Create a ``SettingsItem`` instance compatible with ``TreeModel``."""

    return SettingsItem(
        {
            "id": node_id,
            "id_up": parent_id,
            "type_": "settings_item",
            "prop_name": "name",
            "prop_value": title,
        }
    )


def build_settings_tree() -> List[SettingsItem]:
    """Return the list of settings nodes that populate the dialog tree."""

    root = SettingsNodeDescription(
        "Приложение",
        children=[
            SettingsNodeDescription("Внешний вид"),
        ],
    )

    items: List[SettingsItem] = []
    counter = count(1)

    def add_nodes(description: SettingsNodeDescription, parent_id: int) -> None:
        current_id = next(counter)
        items.append(_create_item(current_id, parent_id, description.title))
        for child in description.iter_children():
            add_nodes(child, current_id)

    add_nodes(root, 0)
    return items


def get_settings_tree() -> List[SettingsItem]:
    """Compatibility wrapper used by the dialog."""

    return build_settings_tree()

