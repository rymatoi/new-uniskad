"""Helpers for switching between the classic and modern application themes."""

from __future__ import annotations

from typing import Optional

from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication


_MODERN_THEME_STYLESHEET = """
QWidget {
    color: #1f2933;
    background-color: #f6f8fb;
    font-family: "Segoe UI", "Inter", "Roboto", sans-serif;
    font-size: 11pt;
}

QMainWindow, QDialog, QDockWidget > QWidget {
    background-color: #f6f8fb;
}

QStatusBar {
    background: #eef2fb;
    color: #1f2933;
    border-top: 1px solid #d5ddee;
}

QStatusBar QLabel {
    color: #52606d;
}

QToolBar {
    background: qlineargradient(y1:0, y2:1, stop:0 #fefeff, stop:1 #edf2ff);
    border: none;
    padding: 8px;
    spacing: 8px;
}

QToolBar QToolButton {
    background-color: #ffffff;
    border: 1px solid #c7d2e8;
    border-radius: 10px;
    padding: 6px 12px;
    color: #1f2933;
}

QToolBar QToolButton:hover {
    background-color: #e4edff;
    border-color: #4f81ff;
}

QToolBar QToolButton:pressed {
    background-color: #d4e2ff;
}

QMenuBar {
    background: #f9fbff;
    border: none;
    padding: 6px 12px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 16px;
    border-radius: 8px;
    color: #1f2933;
}

QMenuBar::item:selected {
    background: #e4edff;
    color: #163dff;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    padding: 10px;
}

QMenu::item {
    padding: 8px 18px;
    border-radius: 6px;
    color: #1f2933;
}

QMenu::item:selected {
    background: #e4edff;
    color: #0f1f5b;
}

QDockWidget {
    titlebar-close-icon: url();
    titlebar-normal-icon: url();
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    background: #ffffff;
}

QDockWidget::title {
    background: qlineargradient(y1:0, y2:1, stop:0 #f2f6ff, stop:1 #e2e8ff);
    border-bottom: 1px solid #c7d2e8;
    padding: 6px 12px;
    font-weight: 600;
    color: #1f2933;
}

QGroupBox {
    border: 1px solid #d5ddee;
    border-radius: 12px;
    margin-top: 16px;
    background: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #52606d;
    background: transparent;
}

QPushButton,
QToolButton,
QCommandLinkButton {
    background-color: #ffffff;
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    padding: 8px 18px;
    color: #1f2933;
    font-weight: 600;
    min-height: 32px;
}

QPushButton:hover,
QToolButton:hover,
QCommandLinkButton:hover {
    background: #e4edff;
    border-color: #4f81ff;
}

QPushButton:pressed,
QToolButton:pressed,
QCommandLinkButton:pressed {
    background: #d4e2ff;
}

QPushButton:disabled,
QToolButton:disabled,
QCommandLinkButton:disabled {
    background: #f0f2f7;
    border-color: #e1e8f4;
    color: #98a2b3;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox,
QComboBox,
QDateEdit,
QDateTimeEdit,
QTimeEdit,
QListView,
QTreeView,
QTableView,
QTableWidget,
QTreeWidget {
    background: #ffffff;
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    padding: 6px 10px;
    selection-background-color: #4f81ff;
    selection-color: #ffffff;
    alternate-background-color: #f4f7ff;
}

QTreeView::item:hover,
QListView::item:hover,
QTableView::item:hover,
QTreeWidget::item:hover {
    background: #e4edff;
}

QTreeView::item:selected,
QListView::item:selected,
QTableView::item:selected,
QTreeWidget::item:selected {
    background: #4f81ff;
    color: #ffffff;
}

QHeaderView::section {
    background: #eef2fb;
    color: #52606d;
    border: none;
    border-right: 1px solid #d5ddee;
    padding: 10px;
    font-weight: 600;
}

QTabWidget::pane {
    border: 1px solid #c7d2e8;
    border-radius: 14px;
    background: #ffffff;
    padding: 8px;
}

QTabBar::tab {
    background: #eef2fb;
    color: #52606d;
    padding: 8px 18px;
    border: 1px solid transparent;
    border-radius: 10px;
    margin: 4px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #1f2933;
    font-weight: 600;
    border: 1px solid #4f81ff;
}

QScrollBar:vertical {
    background: #e6ecfa;
    border: none;
    width: 12px;
    margin: 16px 0 16px 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #4f81ff;
    border-radius: 6px;
    min-height: 24px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 14px;
    background: transparent;
}

QScrollBar:horizontal {
    background: #e6ecfa;
    border: none;
    height: 12px;
    margin: 0 16px 0 16px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #4f81ff;
    border-radius: 6px;
    min-width: 24px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 14px;
    background: transparent;
}

QCheckBox,
QRadioButton {
    spacing: 10px;
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #9aa6c1;
    background: #ffffff;
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    border-color: #4f81ff;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.6, fx:0.5, fy:0.5, stop:0 #ffffff, stop:1 #4f81ff);
}

QProgressBar {
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    background: #ffffff;
    text-align: center;
    color: #1f2933;
}

QProgressBar::chunk {
    background-color: #4f81ff;
    border-radius: 10px;
}

QToolTip {
    background-color: #1f2933;
    color: #ffffff;
    border-radius: 8px;
    padding: 8px 12px;
}

QCalendarWidget QWidget {
    background-color: #ffffff;
}

QSplitter::handle {
    background: #dbe3f5;
    border-radius: 6px;
}

QListWidget,
QTextBrowser {
    background: #ffffff;
    border: 1px solid #c7d2e8;
    border-radius: 12px;
    padding: 8px;
}
"""


_original_palette: Optional[QPalette] = None
_original_stylesheet: Optional[str] = None


def _modern_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f6f8fb"))
    palette.setColor(QPalette.WindowText, QColor("#1f2933"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f4f7ff"))
    palette.setColor(QPalette.Text, QColor("#1f2933"))
    palette.setColor(QPalette.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#1f2933"))
    palette.setColor(QPalette.Highlight, QColor("#4f81ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1f2933"))
    palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.Link, QColor("#3451ff"))
    palette.setColor(QPalette.BrightText, QColor("#e12d39"))
    return palette


def apply_modern_theme(app: Optional[QApplication]) -> None:
    """Apply the modern 2025 light theme to the application."""
    if app is None:
        return

    global _original_palette, _original_stylesheet
    if _original_palette is None:
        _original_palette = QPalette(app.palette())
    if _original_stylesheet is None:
        _original_stylesheet = app.styleSheet()

    app.setPalette(_modern_palette())
    app.setStyleSheet(_MODERN_THEME_STYLESHEET)


def apply_classic_theme(app: Optional[QApplication]) -> None:
    """Restore the original palette and stylesheet."""
    if app is None:
        return

    if _original_palette is not None:
        app.setPalette(_original_palette)
    else:
        app.setPalette(app.style().standardPalette())

    if _original_stylesheet is not None:
        app.setStyleSheet(_original_stylesheet)
    else:
        app.setStyleSheet("")
