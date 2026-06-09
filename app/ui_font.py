"""Central application-wide UI font policy.

Ordinary widgets inherit the QApplication font.  Code that intentionally
provides a local font (for example, a formatted table cell) remains responsible
for returning/setting that override.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from PySide2.QtCore import QEvent
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication, QAbstractItemView

from app import app_logger

logger = app_logger.get_logger(__name__)


def _setting(settings: Any, name: str, default: Any) -> Any:
    if settings is None:
        return default
    if isinstance(settings, Mapping):
        return settings.get(name, default)
    getter = getattr(settings, "get", None)
    return getter(name, default) if getter is not None else default


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    return bool(value)


def configured_application_font(app: QApplication, settings: Any) -> QFont:
    """Build the configured font without changing the application."""
    default_font = getattr(app, "_default_ui_font", None)
    if default_font is None:
        default_font = QFont(app.font())
        app._default_ui_font = QFont(default_font)

    font = QFont(default_font)
    if not _as_bool(_setting(settings, "use_custom_font", False)):
        return font

    family = _setting(settings, "font_name", None)
    if family:
        font.setFamily(str(family))

    try:
        point_size = int(_setting(settings, "font_size", font.pointSize()))
    except (TypeError, ValueError):
        point_size = font.pointSize()
    if point_size > 0:
        font.setPointSize(point_size)

    # Supported for forward compatibility if these settings are exposed later.
    weight = _setting(settings, "font_weight", None)
    if weight is not None:
        try:
            font.setWeight(int(weight))
        except (TypeError, ValueError):
            pass
    bold = _setting(settings, "font_bold", None)
    if bold is not None:
        font.setBold(_as_bool(bold))
    italic = _setting(settings, "font_italic", None)
    if italic is not None:
        font.setItalic(_as_bool(italic))

    return font


def refresh_application_fonts(app: QApplication) -> None:
    """Repolish and redraw existing widgets after QApplication's font changes."""
    event = QEvent(QEvent.ApplicationFontChange)
    for widget in app.allWidgets():
        QApplication.sendEvent(widget, event)
        style = widget.style()
        if style is not None:
            style.unpolish(widget)
            style.polish(widget)
        widget.updateGeometry()
        widget.update()
        if isinstance(widget, QAbstractItemView):
            widget.viewport().update()
            horizontal_header = getattr(widget, "horizontalHeader", None)
            vertical_header = getattr(widget, "verticalHeader", None)
            if callable(horizontal_header):
                horizontal_header().update()
            if callable(vertical_header):
                vertical_header().update()


def apply_application_font(app: QApplication, settings: Any, refresh: bool = True) -> QFont:
    """Apply the configured default font while preserving explicit local fonts."""
    font = configured_application_font(app, settings)
    app.setFont(font)
    if refresh:
        refresh_application_fonts(app)
    logger.info(
        "Applied global UI font: family=%s size=%s weight=%s italic=%s",
        font.family(), font.pointSize(), font.weight(), font.italic(),
    )
    return font

FONT_FORMAT_PROPERTIES = (
    "font_name",
    "font_size",
    "font_bold",
    "font_italic",
    "font_underline",
    "font_strikeout",
)


def _format_value(source: Any, name: str) -> Any:
    if source is None:
        return None
    if isinstance(source, Mapping):
        value = source.get(name)
    else:
        value = getattr(source, name, None)
        # Node defaults use False to mean "not customized". Record mappings
        # retain explicit False values so they can override inherited styles.
        if value is False:
            return None
    if hasattr(value, "prop_value"):
        value = value.prop_value
    return None if value in (None, "") else value


def has_explicit_font_format(*sources: Any) -> bool:
    """Return whether a cell/row/column/node contains an explicit font field."""
    return any(
        _format_value(source, prop) is not None
        for source in sources
        for prop in FONT_FORMAT_PROPERTIES
    )


def explicit_format_font(*sources: Any, base_font: QFont = None):
    """Build a font from explicit formats, using first-source-per-property precedence.

    Returns ``None`` when no source specifies a font property, allowing item views
    to inherit QApplication's font through the normal Qt font policy.
    """
    if not has_explicit_font_format(*sources):
        return None

    if base_font is None:
        app = QApplication.instance()
        base_font = app.font() if app is not None else QFont()
    font = QFont(base_font)

    values = {}
    for prop in FONT_FORMAT_PROPERTIES:
        values[prop] = next(
            (_format_value(source, prop) for source in sources
             if _format_value(source, prop) is not None),
            None,
        )

    if values["font_name"] is not None:
        font.setFamily(str(values["font_name"]))
    if values["font_size"] is not None:
        try:
            size = int(float(values["font_size"]))
            if size > 0:
                font.setPointSize(size)
        except (TypeError, ValueError):
            pass
    for prop, setter in (
        ("font_bold", font.setBold),
        ("font_italic", font.setItalic),
        ("font_underline", font.setUnderline),
        ("font_strikeout", font.setStrikeOut),
    ):
        if values[prop] is not None:
            setter(_as_bool(values[prop]))
    return font
