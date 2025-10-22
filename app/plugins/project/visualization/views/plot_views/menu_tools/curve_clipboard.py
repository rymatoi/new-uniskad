import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.data.adapters.excel_adapter import ExcelDataHandler


@dataclass
class CopiedCurve:
    """Представление данных скопированной кривой."""

    name: str
    points: List[Tuple[float, float]]
    style: Dict[str, Any]
    metadata: Dict[str, Any]


class CurveClipboard:
    """Хранилище данных кривой в буфере обмена."""

    MIME_KEY = "__uniskad_curve__"

    @classmethod
    def copy_curve(cls, curve, project_id: Optional[int] = None) -> None:
        """Сохраняет кривую в системный буфер обмена."""

        points = cls._collect_points(curve)
        style = cls._sanitize_style(getattr(curve, "style_config", {}) or {})
        payload = {
            "type": cls.MIME_KEY,
            "name": curve.name() or "Кривая",
            "points": points,
            "style": style,
            "metadata": {
                "source": "graph",
                "project_id": project_id,
                "copied_from": curve.name() or "",
            },
        }

        clipboard = QApplication.clipboard()
        clipboard.setText(json.dumps(payload))

    @classmethod
    def can_paste(cls) -> bool:
        """Проверяет, содержит ли буфер обмена данные для вставки кривой."""

        return cls.peek() is not None

    @classmethod
    def peek(cls) -> Optional[CopiedCurve]:
        """Возвращает данные кривой из буфера обмена без модификации."""

        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return None

        curve = cls._parse_json_payload(text)
        if curve:
            return curve

        return cls._parse_excel_payload(text)

    @classmethod
    def _parse_json_payload(cls, text: str) -> Optional[CopiedCurve]:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict) or data.get("type") != cls.MIME_KEY:
            return None

        raw_points = data.get("points") or []
        points = cls._normalize_points(raw_points)
        style = cls._merge_styles(data.get("style") or {}, data.get("name"))
        metadata = data.get("metadata") or {}

        if not points:
            return None

        return CopiedCurve(
            name=data.get("name") or metadata.get("copied_from") or "Кривая",
            points=points,
            style=style,
            metadata=metadata,
        )

    @classmethod
    def _parse_excel_payload(cls, text: str) -> Optional[CopiedCurve]:
        try:
            name, values = ExcelDataHandler.parse_clipboard_data(text)
        except Exception:
            return None

        points = cls._normalize_points(values)
        if not points:
            return None

        style = GraphConstants.DEFAULT_STYLE.copy()
        style["name"] = name

        return CopiedCurve(
            name=name,
            points=points,
            style=style,
            metadata={"source": "excel"},
        )

    @staticmethod
    def _collect_points(curve) -> List[List[float]]:
        points: List[List[float]] = []
        x_data = getattr(curve, "xData", [])
        y_data = getattr(curve, "yData", [])
        for x, y in zip(x_data, y_data):
            try:
                points.append([float(x), float(y)])
            except (TypeError, ValueError):
                continue
        return points

    @staticmethod
    def _sanitize_style(style: Dict[str, Any]) -> Dict[str, Any]:
        sanitized: Dict[str, Any] = {}
        for key, value in style.items():
            if isinstance(value, QColor):
                sanitized[key] = value.name()
            elif isinstance(value, (list, tuple)):
                sanitized[key] = list(value)
            elif hasattr(value, "item") and callable(getattr(value, "item")):
                sanitized[key] = value.item()
            else:
                try:
                    json.dumps(value)
                    sanitized[key] = value
                except TypeError:
                    try:
                        sanitized[key] = int(value)
                    except (TypeError, ValueError):
                        try:
                            sanitized[key] = float(value)
                        except (TypeError, ValueError):
                            sanitized[key] = str(value)
        return sanitized

    @staticmethod
    def _normalize_points(values: Sequence[Sequence[Any]]) -> List[Tuple[float, float]]:
        normalized: List[Tuple[float, float]] = []
        for value in values:
            if not isinstance(value, Sequence) or len(value) < 2:
                continue
            try:
                x, y = float(value[0]), float(value[1])
            except (TypeError, ValueError):
                continue
            normalized.append((x, y))
        return normalized

    @staticmethod
    def _merge_styles(style: Dict[str, Any], name: Optional[str]) -> Dict[str, Any]:
        base = GraphConstants.DEFAULT_STYLE.copy()
        base.update(style)
        if name:
            base["name"] = name
        return base
