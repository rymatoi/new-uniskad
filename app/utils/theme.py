"""Utilities for styling the application with a modern light theme."""

from __future__ import annotations

from typing import Optional

from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication, QWidget


MODERN_LIGHT_STYLESHEET = """
* {
    font-family: "Inter", "Segoe UI", "SF Pro Display", "Roboto", sans-serif;
    selection-background-color: #d7deff;
    selection-color: #1f2330;
}

QWidget {
    background-color: #f5f7fb;
    color: #1f2330;
    font-size: 13px;
}

QMainWindow,
QDialog,
QDockWidget > QWidget,
QToolBar {
    background-color: #f5f7fb;
}

QToolTip {
    background-color: #1f2330;
    color: #ffffff;
    border: none;
    padding: 8px 12px;
    border-radius: 8px;
}

QStatusBar {
    background-color: #ffffff;
    color: #4a5161;
    border-top: 1px solid #dbe1f1;
}

QMenuBar,
QMenu {
    background-color: #ffffff;
    border: 1px solid #e5e9f5;
}

QMenuBar {
    border: none;
    padding: 4px 8px;
}

QMenuBar::item,
QMenu::item {
    padding: 6px 12px;
    border-radius: 8px;
}

QMenuBar::item:selected,
QMenu::item:selected {
    background-color: #e9edff;
    color: #1f2330;
}

QMenu::separator {
    height: 1px;
    background: #dbe1f1;
    margin: 4px 12px;
}

QToolBar {
    padding: 10px 16px;
    spacing: 10px;
    border: none;
}

QToolButton,
QPushButton {
    background-color: #ffffff;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 6px 16px;
    color: #1f2330;
    font-weight: 500;
}

QToolButton:hover,
QPushButton:hover {
    border-color: #b8c4ff;
    background-color: #eef1ff;
}

QToolButton:pressed,
QPushButton:pressed {
    background-color: #dce3ff;
    border-color: #9daeff;
}

QToolButton:checked,
QPushButton:checked {
    background-color: #cfd8ff;
    border-color: #7f91ff;
}

QToolButton:disabled,
QPushButton:disabled {
    color: #a0a6b5;
    background-color: #f0f2f8;
    border-color: transparent;
}

QLineEdit,
QPlainTextEdit,
QTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QDateEdit,
QTimeEdit,
QDateTimeEdit,
QAbstractSpinBox,
QListView,
QTreeView,
QTableView {
    background-color: #ffffff;
    border: 1px solid #d5d9e2;
    border-radius: 10px;
    padding: 6px 10px;
    alternate-background-color: #f5f7fb;
}

QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QAbstractSpinBox:focus {
    border: 1px solid #6c63ff;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d5d9e2;
    border-radius: 10px;
    selection-background-color: #e0e5ff;
}

QHeaderView::section {
    background-color: #f0f3ff;
    padding: 6px 12px;
    border: none;
    border-bottom: 1px solid #d5d9e2;
    color: #525b75;
}

QTreeView::item,
QListView::item,
QTableView::item {
    padding: 6px 12px;
    border-radius: 6px;
}

QTreeView::item:selected,
QListView::item:selected,
QTableView::item:selected {
    background-color: #d7deff;
    color: #1f2330;
}

QTableView::item:alternate {
    background-color: #f7f8fc;
}

QDockWidget {
    titlebar-close-icon: url();
    titlebar-normal-icon: url();
    border: 1px solid #dbe1f1;
    border-radius: 12px;
    background-color: #ffffff;
}

QDockWidget::title {
    background-color: #ffffff;
    border: none;
    padding: 8px 12px;
    margin-top: 6px;
    margin-left: 6px;
    margin-right: 6px;
    color: #39405a;
    font-weight: 600;
}

QGroupBox {
    border: 1px solid #dbe1f1;
    border-radius: 12px;
    margin-top: 14px;
    padding: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -8px;
    padding: 0 4px;
    background-color: #f5f7fb;
}

QTabWidget::pane {
    border: 1px solid #dbe1f1;
    border-radius: 12px;
    padding: 10px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #ffffff;
    border: 1px solid transparent;
    padding: 8px 16px;
    border-radius: 10px;
    margin: 4px;
    color: #4a5161;
}

QTabBar::tab:selected {
    background-color: #eef1ff;
    border-color: #b8c4ff;
    color: #1f2330;
}

QScrollBar:vertical {
    width: 12px;
    margin: 10px 4px 10px 0px;
    border: none;
    background-color: transparent;
}

QScrollBar::handle:vertical {
    background-color: #c5cdec;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #aeb7e8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 12px;
    margin: 0px 10px 4px 10px;
    border: none;
    background-color: transparent;
}

QScrollBar::handle:horizontal {
    background-color: #c5cdec;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #aeb7e8;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

QProgressBar {
    border: 1px solid #d5d9e2;
    border-radius: 10px;
    background-color: #ffffff;
    height: 16px;
    text-visible: false;
}

QProgressBar::chunk {
    background-color: #7f91ff;
    border-radius: 8px;
}

QSlider::groove:horizontal {
    height: 6px;
    border-radius: 3px;
    background-color: #d5d9e2;
}

QSlider::handle:horizontal {
    background-color: #ffffff;
    border: 2px solid #7f91ff;
    width: 16px;
    margin: -6px 0;
    border-radius: 10px;
}

QCheckBox,
QRadioButton {
    padding: 4px;
    spacing: 8px;
    color: #38415a;
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #aab3c9;
    border-radius: 6px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    border: 2px solid #7f91ff;
    background-color: #7f91ff;
    border-radius: 6px;
}

QRadioButton::indicator:unchecked {
    border: 2px solid #aab3c9;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    border: 6px solid #7f91ff;
    border-radius: 9px;
    background-color: #ffffff;
}

QCalendarWidget QWidget {
    alternate-background-color: #f5f7fb;
}

QListWidget,
QTreeWidget {
    border-radius: 12px;
    border: 1px solid #dbe1f1;
}

QSplitter::handle {
    background-color: #dbe1f1;
    margin: 2px;
}

QToolBox::tab {
    background-color: #ffffff;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 12px;
    margin-top: 4px;
}

QToolBox::tab:selected {
    border-color: #b8c4ff;
    background-color: #eef1ff;
}
"""


def _standard_palette() -> Optional[QPalette]:
    app = QApplication.instance()
    if not app:
        return None
    return app.style().standardPalette()


def apply_modern_light_theme(widget: QWidget) -> None:
    """Apply the modern light stylesheet and palette to the given widget tree."""

    app = QApplication.instance()
    if app and not hasattr(app, "_uniskad_original_palette"):
        app._uniskad_original_palette = QPalette(app.palette())

    if app:
        palette = QPalette(app.palette())
        palette.setColor(QPalette.Window, QColor("#f5f7fb"))
        palette.setColor(QPalette.WindowText, QColor("#1f2330"))
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#f5f7fb"))
        palette.setColor(QPalette.ToolTipBase, QColor("#1f2330"))
        palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
        palette.setColor(QPalette.Text, QColor("#1f2330"))
        palette.setColor(QPalette.Button, QColor("#ffffff"))
        palette.setColor(QPalette.ButtonText, QColor("#1f2330"))
        palette.setColor(QPalette.Highlight, QColor("#7f91ff"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.PlaceholderText, QColor("#8b93aa"))
        app.setPalette(palette)

    widget.setStyleSheet(MODERN_LIGHT_STYLESHEET)


def clear_modern_theme(widget: QWidget) -> None:
    """Remove the modern stylesheet and restore the original palette."""

    widget.setStyleSheet("")
    app = QApplication.instance()
    if app:
        if hasattr(app, "_uniskad_original_palette"):
            app.setPalette(QPalette(app._uniskad_original_palette))
        else:
            palette = _standard_palette()
            if palette:
                app.setPalette(palette)


