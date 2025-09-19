from app.basic_funcs import timing_decorator
from app.plugins.project.data.exporters.emf_exporter import PlotEMFExporter
from app.plugins.project.data.exporters.excel_exporter import PlotExcelExporter
from app.plugins.project.services.data_processors.plot_dp import PlotProcessor
from app.plugins.project.visualization.views.plot_views.base_plot_view import BasePlotView
import json


class PlotView(BasePlotView):
    DATA_PROCESSOR = PlotProcessor

    def __init__(self, item, main_window, parent=None):
        super().__init__(item, main_window, parent)

    @timing_decorator
    def prepare_curves(self):
        self.clear()
        
        # Загружаем ограничения, если они есть
        has_constraints = False
        if hasattr(self.item, 'graph_constraints') and self.item.graph_constraints:
            try:
                constraints = json.loads(self.item.graph_constraints)
                if constraints:
                    has_constraints = True
                    self.param_constraints = list(constraints.keys())
                    
                    # Получаем данные ограничений
                    test_ids = list(self.data_processor.test_nodes.keys())
                    constraints_data = self.data_processor.data_manager.load_curve_data_array(
                        test_ids, self.param_constraints
                    )
                    
                    # Настраиваем ограничения
                    self.setup_constraint_data(constraints_data)
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Получаем все кривые от процессора данных
        for test_id, x_data, y_data, style in self.data_processor.get_curves():
            # Получаем узел теста
            test_node = self.data_processor.test_nodes.get(test_id)
            if not test_node:
                continue
                
            # Проверяем условия отображения
            if test_node.use_conditions == 'True' and test_node.conditions and test_node.conditions != '[]':
                # Применяем фильтрацию по условиям
                condition_groups = self.filter_by_conditions(x_data, y_data, test_node)
                
                # Для каждой группы создаем отдельную кривую
                for group_key, group_data in condition_groups.items():
                    if group_data['x'] and group_data['y']:
                        # Комбинируем базовый стиль с условным
                        condition_style = style.copy()
                        condition_style.update(group_data['style'])
                        
                        # Создаем кривую
                        curve = self.add_curve(
                            group_data['x'], 
                            group_data['y'], 
                            **condition_style
                        )
                        self.data_processor.register_curve(test_id, curve)
            else:
                # Если есть ограничения - применяем фильтрацию
                if has_constraints:
                    x_filtered, y_filtered = self.filter_by_constraints(x_data, y_data, test_id)
                    
                    # Добавляем кривую только если после фильтрации остались точки
                    if x_filtered and y_filtered:
                        curve = self.add_curve(x_filtered, y_filtered, **style)
                        self.data_processor.register_curve(test_id, curve)
                else:
                    # Если ограничений нет - просто добавляем кривую без изменений
                    curve = self.add_curve(x_data, y_data, **style)
                    self.data_processor.register_curve(test_id, curve)

        # Добавляем пользовательские кривые (без фильтрации)
        for test_id, x, y, style in self.data_processor.get_custom_curves():
            curve = self.add_curve(x, y, **style)
            # Сохраняем ID кастомной кривой, если есть
            if hasattr(style, 'get'):
                custom_curve_id = style.get('custom_curve_id')
                if custom_curve_id:
                    curve.custom_curve_id = custom_curve_id

        # Применяем настройки сетки
        self.apply_grid_settings()

    def export_to_excel(self, filename):
        """Экспортирует данные графика в Excel файл."""
        exporter = PlotExcelExporter()
        exporter.export(self, filename)

    def export_to_emf(self, filename):
        """Экспортирует данные графика в Excel файл."""
        exporter = PlotEMFExporter()
        exporter.export(self, filename)
