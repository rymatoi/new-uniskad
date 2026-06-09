import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide2")

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication, QLabel

from app.ui_font import apply_application_font, explicit_format_font, has_explicit_font_format


def application():
    return QApplication.instance() or QApplication([])


def test_application_font_applies_to_existing_and_new_widgets():
    app = application()
    original = QFont(app.font())
    existing = QLabel("existing")
    try:
        applied = apply_application_font(app, {
            "use_custom_font": True,
            "font_name": "DejaVu Sans",
            "font_size": 17,
        })
        created_after = QLabel("new")

        assert applied.pointSize() == 17
        assert existing.font().pointSize() == 17
        assert created_after.font().pointSize() == 17
    finally:
        app.setFont(original)


def test_explicit_format_font_returns_none_for_unformatted_content():
    assert not has_explicit_font_format({}, {})
    assert explicit_format_font({}, {}) is None


def test_explicit_format_font_uses_source_precedence_and_global_defaults():
    app = application()
    original = QFont(app.font())
    base = QFont(original)
    base.setFamily("DejaVu Sans")
    base.setPointSize(13)
    app.setFont(base)
    try:
        font = explicit_format_font(
            {"font_bold": "True"},
            {"font_size": "18", "font_bold": "False"},
            {"font_name": "DejaVu Serif"},
        )
        assert font.family() == "DejaVu Serif"
        assert font.pointSize() == 18
        assert font.bold()
    finally:
        app.setFont(original)
