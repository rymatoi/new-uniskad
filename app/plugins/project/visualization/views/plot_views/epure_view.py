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
            self.plotItem.legend.addItem(epure.legend_proxy, epure.name())

        return epure

    @timing_decorator
    def prepare_curves(self):
        self.clear()
        for scatter_values, curve_values, style in self.data_processor.get_epure_curves():
            self.add_curve(scatter_values, curve_values, **style)
