"""Application-wide visual refinements that leave the active palette untouched."""

from PySide6.QtWidgets import QProxyStyle, QStyle


CONTAINER_STYLE_SHEET = """
/* Keep neighbouring work areas legible without imposing a light or dark theme. */
QMainWindow::separator {
    background: palette(mid);
    width: 2px;
    height: 2px;
}

QSplitter::handle {
    background: palette(mid);
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QDockWidget, QMdiSubWindow {
    border: 1px solid palette(mid);
}

QDockWidget::title {
    background: palette(alternate-base);
    border-bottom: 1px solid palette(mid);
    padding: 6px 8px;
}

QDockWidget > QWidget#dockTitleBar {
    background: palette(alternate-base);
    border-bottom: 1px solid palette(mid);
}

QTabWidget::pane {
    border: 1px solid palette(mid);
}

QGroupBox {
    border: 1px solid palette(mid);
    border-radius: 3px;
    margin-top: 0.7em;
    padding-top: 0.5em;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
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
