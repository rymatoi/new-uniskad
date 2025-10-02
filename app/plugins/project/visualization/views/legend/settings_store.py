from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple

from PySide2.QtCore import QSettings
from PySide2.QtGui import QColor

ORGANIZATION = "Uniskad"
APPLICATION = "NewUniskad"
SETTINGS_GROUP = "Legend"
OFFSET_X_KEY = "offset_x"
OFFSET_Y_KEY = "offset_y"


def default_legend_settings() -> Dict[str, object]:
    """Возвращает набор настроек легенды по умолчанию."""
    return {
        "background_color": QColor(255, 255, 255),
        "background_opacity": 100,
        "border_color": QColor(100, 100, 100),
        "border_width": 1,
    }


def _coerce_color(value: Any, fallback: QColor) -> QColor:
    if isinstance(value, QColor):
        return QColor(value)

    if isinstance(value, str):
        color = QColor(value)
        if color.isValid():
            return color

    if isinstance(value, (tuple, list)):
        try:
            color = QColor(*value)
        except TypeError:
            color = QColor()
        if color.isValid():
            return color

    if isinstance(value, int):
        color = QColor()
        color.setRgba(value)
        if color.isValid():
            return color

    return QColor(fallback)


def _coerce_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def normalize_legend_settings(overrides: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Объединяет настройки с умолчаниями и приводит типы."""
    result = default_legend_settings()

    if not overrides:
        return result

    if "background_color" in overrides:
        result["background_color"] = _coerce_color(
            overrides["background_color"], result["background_color"]
        )

    if "border_color" in overrides:
        result["border_color"] = _coerce_color(
            overrides["border_color"], result["border_color"]
        )

    if "background_opacity" in overrides:
        opacity = _coerce_int(overrides["background_opacity"], result["background_opacity"])
        result["background_opacity"] = max(0, min(100, opacity))

    if "border_width" in overrides:
        width = _coerce_int(overrides["border_width"], result["border_width"])
        result["border_width"] = max(0, width)

    return result


def load_legend_settings(overrides: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Загружает настройки легенды из QSettings, дополняя переданными значениями."""
    base = normalize_legend_settings(overrides)

    qsettings = QSettings(ORGANIZATION, APPLICATION)
    qsettings.beginGroup(SETTINGS_GROUP)

    stored: Dict[str, object] = {}
    for key in ("background_color", "background_opacity", "border_color", "border_width"):
        value = qsettings.value(key, None)
        if value is not None:
            stored[key] = value

    qsettings.endGroup()

    if stored:
        base = normalize_legend_settings({**base, **stored})

    return base


def save_legend_settings(settings: Dict[str, object]) -> Dict[str, object]:
    """Сохраняет настройки легенды в QSettings и возвращает нормализованный вариант."""
    normalized = normalize_legend_settings(settings)

    qsettings = QSettings(ORGANIZATION, APPLICATION)
    qsettings.beginGroup(SETTINGS_GROUP)
    qsettings.setValue("background_color", normalized["background_color"].name(QColor.HexRgb))
    qsettings.setValue("background_opacity", int(normalized["background_opacity"]))
    qsettings.setValue("border_color", normalized["border_color"].name(QColor.HexRgb))
    qsettings.setValue("border_width", int(normalized["border_width"]))
    qsettings.endGroup()
    qsettings.sync()

    return normalized


def _coerce_offset(value: Any) -> Optional[Tuple[float, float]]:
    if value is None:
        return None

    if isinstance(value, (tuple, list)):
        if len(value) >= 2:
            try:
                return float(value[0]), float(value[1])
            except (TypeError, ValueError):
                return None
        return None

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        try:
            first, second = value[0], value[1]
        except IndexError:
            return None
        try:
            return float(first), float(second)
        except (TypeError, ValueError):
            return None

    if hasattr(value, "x") and hasattr(value, "y"):
        try:
            return float(value.x()), float(value.y())
        except TypeError:
            return None

    return None


def load_legend_offset(default: Optional[Tuple[float, float]] = None) -> Optional[Tuple[float, float]]:
    """Загружает сохраненный сдвиг легенды из QSettings."""
    qsettings = QSettings(ORGANIZATION, APPLICATION)
    qsettings.beginGroup(SETTINGS_GROUP)
    x_value = qsettings.value(OFFSET_X_KEY, None, type=float)
    y_value = qsettings.value(OFFSET_Y_KEY, None, type=float)
    qsettings.endGroup()

    if x_value is None or y_value is None:
        return default

    try:
        return float(x_value), float(y_value)
    except (TypeError, ValueError):
        return default


def save_legend_offset(offset: Any) -> None:
    """Сохраняет сдвиг легенды в QSettings."""
    coords = _coerce_offset(offset)
    if coords is None:
        return

    qsettings = QSettings(ORGANIZATION, APPLICATION)
    qsettings.beginGroup(SETTINGS_GROUP)
    qsettings.setValue(OFFSET_X_KEY, coords[0])
    qsettings.setValue(OFFSET_Y_KEY, coords[1])
    qsettings.endGroup()
    qsettings.sync()
