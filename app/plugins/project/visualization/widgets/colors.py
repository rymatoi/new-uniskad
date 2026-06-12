"""Safe conversion of stored project style colors to ``QColor``."""

import pyqtgraph as pg
from PySide2.QtGui import QColor

from app import app_logger


logger = app_logger.get_logger(__name__)

# ProjectData can contain Qt enum names that pyqtgraph does not recognize.
NAMED_COLORS = {
    'red': '#ff0000',
    'green': '#00ff00',
    'blue': '#0000ff',
    'cyan': '#00ffff',
    'magenta': '#ff00ff',
    'yellow': '#ffff00',
    'darkred': '#800000',
    'darkgreen': '#008000',
    'darkblue': '#000080',
    'darkcyan': '#008080',
    'darkmagenta': '#800080',
    'darkyellow': '#808000',
    'darkgray': '#808080',
    'gray': '#a0a0a4',
    'lightgray': '#c0c0c0',
}

_warned_fallback_values = set()


def _warn_fallback_once(color_value, fallback):
    """Log each unsupported stored value once, not once per plotted item."""
    key = (type(color_value).__name__, repr(color_value))
    if key in _warned_fallback_values:
        return
    _warned_fallback_values.add(key)
    logger.warning(
        "Unable to convert project graph color %r; using fallback %r",
        color_value,
        fallback,
    )


def safe_color(color_value, fallback, *, force_opaque=False, allow_transparent=False):
    """Return a valid QColor, safely replacing unsupported values.

    ``allow_transparent`` preserves the existing CurveItem behavior where the
    string values ``none`` and ``transparent`` disable a symbol color.
    """
    if (
        allow_transparent
        and isinstance(color_value, str)
        and color_value.lower() in {'none', 'transparent'}
    ):
        return None

    candidate = color_value
    if isinstance(candidate, str):
        candidate = NAMED_COLORS.get(candidate.lower(), candidate)

    color = None
    if candidate is not None and candidate != '':
        try:
            color = pg.mkColor(candidate)
        except Exception:  # pyqtgraph raises different conversion errors by value/type
            color = None

    if color is None or not color.isValid():
        if color_value is not None:
            _warn_fallback_once(color_value, fallback)
        try:
            color = pg.mkColor(fallback)
        except Exception:
            # The application fallback is controlled by code, but keep this
            # path safe if a future style configuration accidentally breaks it.
            color = QColor(0, 0, 0)

    if not color.isValid():
        color = QColor(0, 0, 0)

    if force_opaque:
        color.setAlpha(255)
    return color
