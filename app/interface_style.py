"""Application-wide visual refinements that leave the active palette untouched."""

from PySide6.QtWidgets import QProxyStyle, QStyle


CONTAINER_STYLE_SHEET = """
/*
 * Separate major work areas with calm background-coloured gutters rather than
 * high-contrast rules.  The palette roles keep this equally restrained in
 * light and dark system themes.
 */
QMainWindow::separator {
    background: palette(window);
    width: 6px;
    height: 6px;
}

QMainWindow::separator:hover {
    background: palette(midlight);
}

QSplitter::handle {
    background: palette(window);
}

QSplitter::handle:hover {
    background: palette(midlight);
}

QSplitter::handle:horizontal {
    width: 6px;
}

QSplitter::handle:vertical {
    height: 6px;
}

/* Containers stay distinct without boxing every part of the workspace. */
QDockWidget {
    border: none;
}

QMdiSubWindow {
    border: 1px solid palette(midlight);
}

QDockWidget::title {
    background: palette(window);
    border-bottom: 1px solid palette(midlight);
    padding: 7px 9px;
}

QDockWidget > QWidget#dockTitleBar {
    background: palette(window);
    border-bottom: 1px solid palette(midlight);
}

QTabWidget::pane {
    border: 1px solid palette(midlight);
}

QTabBar::tab {
    padding: 7px 12px;
}

QGroupBox {
    border: 1px solid palette(midlight);
    border-radius: 2px;
    margin-top: 0.8em;
    padding-top: 0.6em;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}

/* Quiet, precise chrome gives dense data screens a stricter hierarchy. */
QToolBar {
    border: none;
    border-bottom: 1px solid palette(midlight);
    spacing: 4px;
}

QHeaderView::section {
    border: none;
    border-right: 1px solid palette(midlight);
    border-bottom: 1px solid palette(midlight);
    padding: 5px 7px;
}

QStatusBar {
    border-top: 1px solid palette(midlight);
}
"""


class FriendlyProxyStyle(QProxyStyle):
    """Make standard controls a little less cramped without replacing their style."""

    _MINIMUM_METRICS = {
        QStyle.PixelMetric.PM_ButtonMargin: 8,
        QStyle.PixelMetric.PM_LayoutHorizontalSpacing: 6,
        QStyle.PixelMetric.PM_LayoutVerticalSpacing: 6,
        QStyle.PixelMetric.PM_TabBarTabHSpace: 16,
        QStyle.PixelMetric.PM_TabBarTabVSpace: 8,
        QStyle.PixelMetric.PM_ToolBarItemSpacing: 4,
    }

    def pixelMetric(self, metric, option=None, widget=None):
        value = super().pixelMetric(metric, option, widget)
        minimum = self._MINIMUM_METRICS.get(metric)
        return max(value, minimum) if minimum is not None else value
