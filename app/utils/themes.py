"""Application-wide visual themes."""
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication


class ModernLightTheme:
    """Collection of helpers for the 2025-inspired light interface."""

    PRIMARY_COLOR = "#3478f6"
    PRIMARY_HOVER = "#4d8bff"
    PRIMARY_ACTIVE = "#1f63e0"
    SURFACE_COLOR = "#ffffff"
    BASE_COLOR = "#f4f6fb"
    BORDER_COLOR = "#dfe3eb"
    BORDER_COLOR_DARK = "#bfc8d9"
    TEXT_COLOR = "#1c1f26"
    SUBTEXT_COLOR = "#556072"

    @classmethod
    def stylesheet(cls) -> str:
        """Return the stylesheet that styles the modern interface."""
        return f"""
        * {{
            font-family: "Inter", "Segoe UI", "Noto Sans", "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            color: {cls.TEXT_COLOR};
        }}
        QWidget {{
            background-color: {cls.BASE_COLOR};
        }}
        QMainWindow, QDialog, QFrame, QStackedWidget, QToolBox {{
            background-color: {cls.BASE_COLOR};
        }}
        QToolTip {{
            background-color: {cls.SURFACE_COLOR};
            color: {cls.TEXT_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            padding: 6px 10px;
            border-radius: 6px;
        }}
        QMenuBar {{
            background-color: {cls.SURFACE_COLOR};
            border-bottom: 1px solid {cls.BORDER_COLOR};
            padding: 4px 8px;
        }}
        QMenuBar::item {{
            background: transparent;
            padding: 6px 12px;
            margin: 2px 4px;
            border-radius: 8px;
        }}
        QMenuBar::item:selected {{
            background-color: rgba(52, 120, 246, 0.15);
        }}
        QMenu {{
            background-color: {cls.SURFACE_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 12px;
            padding: 8px;
        }}
        QMenu::item {{
            padding: 8px 18px;
            border-radius: 6px;
            margin: 2px 0;
        }}
        QMenu::item:selected {{
            background-color: rgba(52, 120, 246, 0.12);
        }}
        QToolBar {{
            background-color: {cls.SURFACE_COLOR};
            border: none;
            padding: 10px;
            spacing: 8px;
        }}
        QToolBar::separator {{
            width: 1px;
            background: {cls.BORDER_COLOR};
            margin: 0 6px;
        }}
        QStatusBar {{
            background-color: {cls.SURFACE_COLOR};
            border-top: 1px solid {cls.BORDER_COLOR};
        }}
        QStatusBar::item {{
            border: none;
        }}
        QStatusBar QLabel {{
            color: {cls.SUBTEXT_COLOR};
        }}
        QDockWidget {{
            background: {cls.SURFACE_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 12px;
        }}
        QDockWidget::title {{
            background: linear-gradient(180deg, #ffffff, #f1f5ff);
            padding: 8px 12px;
            border-bottom: 1px solid {cls.BORDER_COLOR};
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }}
        QDockWidget QWidget {{
            background: {cls.SURFACE_COLOR};
        }}
        QGroupBox {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 12px;
            margin-top: 12px;
            padding: 12px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 6px;
            color: {cls.SUBTEXT_COLOR};
        }}
        QPushButton {{
            background-color: {cls.PRIMARY_COLOR};
            border: 1px solid {cls.PRIMARY_COLOR};
            color: #ffffff;
            border-radius: 10px;
            padding: 8px 18px;
            font-weight: 600;
            min-height: 34px;
        }}
        QPushButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
            border-color: {cls.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {cls.PRIMARY_ACTIVE};
            border-color: {cls.PRIMARY_ACTIVE};
        }}
        QPushButton:checked {{
            background-color: {cls.PRIMARY_ACTIVE};
            border-color: {cls.PRIMARY_ACTIVE};
            color: #ffffff;
        }}
        QPushButton:disabled {{
            background-color: #e0e7f9;
            border-color: #e0e7f9;
            color: #98a5bf;
        }}
        QPushButton:flat {{
            background: transparent;
            border: none;
            color: {cls.PRIMARY_COLOR};
            font-weight: 600;
        }}
        QPushButton:flat:hover {{
            background-color: rgba(52, 120, 246, 0.1);
            border-radius: 8px;
        }}
        QToolButton {{
            background: {cls.SURFACE_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 10px;
            padding: 6px 12px;
        }}
        QToolButton:hover {{
            border-color: {cls.BORDER_COLOR_DARK};
            background: #f2f5ff;
        }}
        QToolButton:pressed {{
            background: #e4ecff;
        }}
        QToolButton:checked {{
            background: rgba(52, 120, 246, 0.18);
            border-color: {cls.PRIMARY_COLOR};
            color: {cls.PRIMARY_COLOR};
        }}
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit,
        QPlainTextEdit, QTextEdit, QAbstractSpinBox {{
            background: {cls.SURFACE_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 10px;
            padding: 6px 12px;
            selection-background-color: {cls.PRIMARY_COLOR};
            selection-color: #ffffff;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus,
        QDateTimeEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {cls.PRIMARY_COLOR};
        }}
        QComboBox::drop-down {{
            width: 32px;
            border-left: 1px solid {cls.BORDER_COLOR};
            background: transparent;
        }}
        QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
            background: transparent;
            border: none;
            width: 20px;
            margin: 2px;
        }}
        QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{
            background: rgba(52, 120, 246, 0.08);
            border-radius: 6px;
        }}
        QTreeView, QTreeWidget, QListView, QListWidget, QTableView, QTableWidget {{
            background: {cls.SURFACE_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 10px;
            alternate-background-color: #f7f9ff;
            selection-color: #ffffff;
            selection-background-color: {cls.PRIMARY_COLOR};
            gridline-color: {cls.BORDER_COLOR};
        }}
        QTreeView::item, QListView::item {{
            padding: 6px 12px;
        }}
        QTreeView::item:hover, QListView::item:hover {{
            background: rgba(52, 120, 246, 0.08);
        }}
        QHeaderView::section {{
            background: #f1f5ff;
            color: {cls.SUBTEXT_COLOR};
            padding: 8px 12px;
            border: none;
            border-right: 1px solid {cls.BORDER_COLOR};
        }}
        QHeaderView::section:last {{
            border-right: none;
        }}
        QTableView QTableCornerButton::section {{
            background: #f1f5ff;
            border: none;
        }}
        QTabWidget::pane {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 12px;
            background: {cls.SURFACE_COLOR};
            margin-top: 8px;
        }}
        QTabBar::tab {{
            background: transparent;
            padding: 10px 18px;
            margin-right: 6px;
            border: none;
            border-bottom: 2px solid transparent;
            color: {cls.SUBTEXT_COLOR};
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            color: {cls.TEXT_COLOR};
            border-bottom: 2px solid {cls.PRIMARY_COLOR};
        }}
        QTabBar::tab:hover {{
            color: {cls.PRIMARY_COLOR};
        }}
        QProgressBar {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 10px;
            text-align: center;
            background: {cls.SURFACE_COLOR};
        }}
        QProgressBar::chunk {{
            background-color: {cls.PRIMARY_COLOR};
            border-radius: 8px;
        }}
        QSlider::groove:horizontal {{
            height: 6px;
            background: {cls.BORDER_COLOR};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {cls.PRIMARY_COLOR};
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        QSlider::groove:vertical {{
            width: 6px;
            background: {cls.BORDER_COLOR};
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: {cls.PRIMARY_COLOR};
            height: 18px;
            margin: 0 -6px;
            border-radius: 9px;
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QSplitter::handle {{
            background: {cls.BORDER_COLOR};
            border-radius: 4px;
        }}
        QSplitter::handle:pressed {{
            background: {cls.PRIMARY_COLOR};
        }}
        QScrollBar:vertical {{
            width: 12px;
            background: transparent;
            margin: 6px 0 6px 0;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(52, 120, 246, 0.35);
            min-height: 40px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: rgba(52, 120, 246, 0.5);
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
            border: none;
        }}
        QScrollBar:horizontal {{
            height: 12px;
            background: transparent;
            margin: 0 6px 0 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: rgba(52, 120, 246, 0.35);
            min-width: 40px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: rgba(52, 120, 246, 0.5);
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
            border: none;
        }}
        QCheckBox, QRadioButton {{
            spacing: 8px;
            color: {cls.TEXT_COLOR};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 6px;
            border: 1px solid {cls.BORDER_COLOR};
            background: {cls.SURFACE_COLOR};
        }}
        QCheckBox::indicator:checked {{
            border: 1px solid {cls.PRIMARY_COLOR};
            background-color: {cls.PRIMARY_COLOR};
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 9px;
            background: {cls.SURFACE_COLOR};
        }}
        QRadioButton::indicator:checked {{
            border: 5px solid {cls.PRIMARY_COLOR};
        }}
        QCalendarWidget QWidget {{
            background: {cls.SURFACE_COLOR};
        }}
        QCalendarWidget QToolButton {{
            min-height: 28px;
        }}
        QLabel[secondary="true"], QAbstractItemView::item:selected:!active {{
            color: #ffffff;
        }}
        """

    @classmethod
    def apply_palette(cls, app: QApplication) -> None:
        """Apply a bright palette that matches the stylesheet."""
        palette = app.style().standardPalette()
        palette.setColor(QPalette.Window, QColor(cls.BASE_COLOR))
        palette.setColor(QPalette.WindowText, QColor(cls.TEXT_COLOR))
        palette.setColor(QPalette.Base, QColor(cls.SURFACE_COLOR))
        palette.setColor(QPalette.AlternateBase, QColor("#f7f9ff"))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.SURFACE_COLOR))
        palette.setColor(QPalette.ToolTipText, QColor(cls.TEXT_COLOR))
        palette.setColor(QPalette.Text, QColor(cls.TEXT_COLOR))
        palette.setColor(QPalette.Button, QColor(cls.SURFACE_COLOR))
        palette.setColor(QPalette.ButtonText, QColor(cls.TEXT_COLOR))
        palette.setColor(QPalette.BrightText, QColor("#ff4b55"))
        palette.setColor(QPalette.Highlight, QColor(cls.PRIMARY_COLOR))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.PlaceholderText, QColor(cls.SUBTEXT_COLOR))
        app.setPalette(palette)

    @classmethod
    def reset_palette(cls, app: QApplication) -> None:
        """Return application palette to the style defaults."""
        app.setPalette(app.style().standardPalette())
