"""Application-wide visual refinements that leave the active palette untouched."""

from PySide6.QtWidgets import QProxyStyle, QStyle


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
