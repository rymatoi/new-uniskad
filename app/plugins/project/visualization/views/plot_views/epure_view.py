from app.basic_funcs import timing_decorator
from app.plugins.project.services.data_processors.epure_dp import EpureProcessor
from app.plugins.project.visualization.views.plot_views.base_plot_view import BasePlotView
from app.plugins.project.visualization.widgets.epure import EpureItem


class EpureView(BasePlotView):
    DATA_PROCESSOR = EpureProcessor

    def __init__(self, item, main_window, parent=None):
        super().__init__(item, main_window, parent)

    def add_curve(self, scatter_data, plot_data, **style):
        epure = EpureItem(scatter_data, plot_data, style=style)
        self.addItem(epure)
        self.curve_items.append(epure)
        self.selected_points[epure] = set()

        if hasattr(self.plotItem, 'legend') and self.plotItem.legend is not None:
            self._replace_epure_legend_item(epure)

        return epure

    def _replace_epure_legend_item(self, epure: EpureItem) -> None:
        legend = getattr(self.plotItem, 'legend', None)

        if legend is None:
            return

        legend_name = epure.name()
        related_items = {epure.legend_proxy, getattr(epure, 'curve', None), getattr(epure, 'scatter', None)}

        removed = False
        for sample, label in list(legend.items):
            sample_item = getattr(sample, 'item', None)
            label_text = ''

            if hasattr(label, 'toPlainText'):
                label_text = label.toPlainText()
            elif hasattr(label, 'text'):
                text_value = label.text
                label_text = text_value() if callable(text_value) else text_value

            if sample_item in related_items or label_text == legend_name:
                legend.items.remove((sample, label))
                sample.setParentItem(None)
                label.setParentItem(None)
                removed = True

        if removed and hasattr(legend, 'updateSize'):
            legend.updateSize()

        legend.addItem(epure.legend_proxy, legend_name)

    @timing_decorator
    def prepare_curves(self):
        self.clear()
        for scatter_values, curve_values, style in self.data_processor.get_epure_curves():
            self.add_curve(scatter_values, curve_values, **style)
