"""Public Project utility API.

Keep compatibility with callers importing ``app.plugins.project.utils`` while
the legacy implementations remain in ``utils_.py``.
"""

from app.plugins.project.utils_ import COLORS, LINE_STYLES, SYMBOLS, get_next_default_combination

__all__ = ['COLORS', 'LINE_STYLES', 'SYMBOLS', 'get_next_default_combination']
