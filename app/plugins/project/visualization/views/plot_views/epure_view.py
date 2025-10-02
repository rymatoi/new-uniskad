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

        legend = getattr(self.plotItem, 'legend', None)
        if legend is not None:
            self._register_epure_in_legend(epure, legend)
        return epure

    @timing_decorator
    def prepare_curves(self):
        self.clear()
        for scatter_values, curve_values, style in self.data_processor.get_epure_curves():
            self.add_curve(scatter_values, curve_values, **style)

    def _register_epure_in_legend(self, epure: EpureItem, legend):
        """Заменяет записи легенды для эпюры на прокси-элемент."""
        # Удаляем автоматически добавленные элементы для scatter/curve, если они есть
        items_to_remove = []
        for sample, _label in list(getattr(legend, 'items', [])):
            linked_item = getattr(sample, 'item', None)
            if linked_item in (epure.curve, epure.scatter, epure.legend_proxy):
                items_to_remove.append(linked_item)

        for item in items_to_remove:
            legend.removeItem(item)

        # Добавляем прокси-элемент, который будет управлять видимостью обеих частей эпюры
        legend.addItem(epure.legend_proxy, epure.name())
