from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication, QWidget


_ROOT_DIR = Path(__file__).resolve().parent.parent
_STYLE_PATH = _ROOT_DIR / "resources" / "styles" / "modern_light.qss"


def coerce_to_bool(value: Any, default: bool = False) -> bool:
    """Safely cast the stored user preference to :class:`bool`."""
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
        return default
    return bool(value)


@lru_cache(maxsize=1)
def _load_stylesheet() -> str:
    try:
        return _STYLE_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _apply_modern_palette(app: QApplication) -> None:
    palette = QPalette(app.palette())
    palette.setColor(QPalette.Window, QColor("#f4f7fb"))
    palette.setColor(QPalette.WindowText, QColor("#1f2d5c"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f5f8ff"))
    palette.setColor(QPalette.Text, QColor("#1f2d5c"))
    palette.setColor(QPalette.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#1f2d5c"))
    palette.setColor(QPalette.Highlight, QColor("#6f8bff"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor("#1f2337"))
    app.setPalette(palette)


def apply_modern_theme(enabled: bool, *, base_widget: Optional[QWidget] = None) -> None:
    """Enable or disable the modern light interface theme."""
    app = QApplication.instance()
    if app is None:
        return

    enabled = bool(enabled)
    app.setProperty("modern_ui_enabled", enabled)

    if enabled:
        stylesheet = _load_stylesheet()
        app.setStyleSheet(stylesheet)
        _apply_modern_palette(app)
    else:
        app.setStyleSheet("")
        app.setPalette(app.style().standardPalette())

    if base_widget is not None:
        base_widget.setProperty("modern_ui_enabled", enabled)
        base_widget.style().unpolish(base_widget)
        base_widget.style().polish(base_widget)

    for widget in app.allWidgets():
        if not isinstance(widget, QWidget):
            continue
        widget.setProperty("modern_ui_enabled", enabled)
        style = widget.style()
        if style is not None:
            style.unpolish(widget)
            style.polish(widget)
        widget.update()
