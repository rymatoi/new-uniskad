from app.basic_funcs import timing_decorator
from app.plugins.project.services.data_processors.epure_dp import EpureProcessor
from app.plugins.project.visualization.views.plot_views.base_plot_view import BasePlotView
from app.plugins.project.visualization.views.plot_views.mixins.plot_data import PlotDataMixin
from app.plugins.project.visualization.widgets.epure import EpureItem


class EpureView(BasePlotView):
    DATA_PROCESSOR = EpureProcessor

    def __init__(self, item, main_window, parent=None):
        self._epure_items = {}
        super().__init__(item, main_window, parent)

    def clear(self):
        super().clear()
        if self.legend is not None:
            self.legend.clear()
        self._epure_items.clear()
        self.curve_items.clear()
        self.selected_points.clear()

    def _remove_epure(self, test_id):
        epure = self._epure_items.pop(test_id, None)
        if epure is None:
            return

        if self.legend is not None and self.legend.items:
            for index, (sample, label) in enumerate(list(self.legend.items)):
                if getattr(sample, 'item', None) == epure.legend_proxy:
                    self.legend.items.pop(index)
                    sample.setParentItem(None)
                    label.setParentItem(None)
                    break

        if epure in self.curve_items:
            self.curve_items.remove(epure)
        self.selected_points.pop(epure, None)
        self.removeItem(epure)

    def _update_legend_label(self, epure: EpureItem) -> None:
        if self.legend is None or not self.legend.items:
            return

        for sample, label in self.legend.items:
            if getattr(sample, 'item', None) == epure.legend_proxy:
                label.setText(epure.name())
                break

    def _upsert_epure(self, test_id, scatter_data, plot_data, style):
        epure = self._epure_items.get(test_id)
        if epure is None:
            epure = EpureItem(scatter_data, plot_data, style=style)
            self._epure_items[test_id] = epure
            self.addItem(epure)
            self.curve_items.append(epure)
            self.selected_points[epure] = set()
            if self.legend is not None:
                self.legend.addItem(epure.legend_proxy, epure.name())
        else:
            was_visible = epure.isVisible()
            proxy_visible = epure.legend_proxy.isVisible()
            epure.update_data(scatter_data, plot_data, style=style)
            epure.setVisible(was_visible)
            epure.legend_proxy.setVisible(proxy_visible)
            self._update_legend_label(epure)
        return epure

    def add_curve(self, scatter_data, plot_data, **style):
        test_id = style.pop('test_id', None)
        if test_id is None:
            # Для совместимости с миксинами, которые могут ожидать стандартное поведение
            return PlotDataMixin.add_curve(self, scatter_data, plot_data, **style)
        return self._upsert_epure(test_id, scatter_data, plot_data, style)

    def _sync_epures(self, entries, remove_missing=True):
        seen_ids = set()
        for test_id, scatter_values, curve_values, style in entries:
            seen_ids.add(test_id)
            self._upsert_epure(test_id, scatter_values, curve_values, style)

        if remove_missing:
            stale_ids = set(self._epure_items.keys()) - seen_ids
            for test_id in stale_ids:
                self._remove_epure(test_id)

    @timing_decorator
    def prepare_curves(self):
        epure_entries = list(self.data_processor.get_epure_curves())
        self._sync_epures(epure_entries, remove_missing=True)

    def _update_curves(self, test_ids):
        if test_ids is None:
            self.prepare_curves()
            return

        requested_ids = set(test_ids)
        epure_entries = [
            entry for entry in self.data_processor.get_epure_curves()
            if entry[0] in requested_ids
        ]
        if epure_entries:
            self._sync_epures(epure_entries, remove_missing=False)
