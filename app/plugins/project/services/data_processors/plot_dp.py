from app.plugins.project.data.datamanagers.graph_datamanager import GraphDataManager
from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.base_dp import DataProcessor
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.utils.collectors import PlotDataCollector as Collector
from typing import Dict, List, Optional
from app.plugins.project.visualization.widgets.curve import CurveItem
import json


class PlotProcessor(DataProcessor):
    DATA_MANAGER = GraphDataManager

    def __init__(self, item):
        super().__init__(item)
        self.test_nodes = self.load_test_nodes(item)
        self.plot_data = self.init_plot_data(item)
        self.other_data = self.init_other_data()
        self.curve_map: Dict[int, CurveItem] = {}  # test_id -> curve

    def init_plot_data(self, item):
        x_param = ItemProcessor.get_x_param(item)
        y_param = ItemProcessor.get_y_param(item)
        test_id_list = self.test_nodes.keys()

        x_data = self.data_manager.load_curve_data(test_id_list, x_param)
        y_data = self.data_manager.load_curve_data(test_id_list, y_param)

        return Collector.process_plot_values(x_data, y_data, x_param, y_param)

    def init_other_data(self):
        custom_curves = self.data_manager.load_custom_curves()
        return custom_curves

    @staticmethod
    def load_test_nodes(item):
        return TestProcessor.collect_tests(item)

    def get_curves(self):
        """Получение данных для кривых"""
        curves_data = ItemProcessor.get_plot_data(self.plot_data, self.test_nodes)
        for test_id, x, y, style in curves_data:
            yield test_id, x, y, style

    def get_custom_curves(self):
        """Получение данных для пользовательских кривых"""

        approx_curves = []
        custom_curves = []

        for curve in self.other_data:
            raw_values = curve.values
            try:
                curve_data = json.loads(raw_values) if isinstance(raw_values, str) else raw_values
            except json.JSONDecodeError:
                continue

            if isinstance(curve_data, dict) and 'test_id' in curve_data:
                approx_curves.append(curve)
            elif isinstance(curve_data, dict) and 'values' in curve_data:
                custom_curves.append((curve, curve_data))

        curves_data = ItemProcessor.get_other_data(self.plot_data, approx_curves, self.test_nodes)
        remaining_curves = list(approx_curves)

        for test_id, x, y, style in curves_data:
            curve_name = style.get('name', '')
            curve_type = style.get('type', '')
            curve_degree = style.get('degree', None)

            best_match = None
            best_match_index = -1

            for i, curve in enumerate(remaining_curves):
                raw_values = curve.values
                curve_data = json.loads(raw_values) if isinstance(raw_values, str) else raw_values

                if curve_data.get('test_id') != test_id or curve_data.get('name') != curve_name:
                    continue

                curve_matches = True

                if curve_type and 'type' in curve_data and curve_data.get('type') != curve_type:
                    curve_matches = False

                if curve_degree is not None and 'degree' in curve_data and curve_data.get('degree') != curve_degree:
                    curve_matches = False

                if curve_matches:
                    best_match = curve
                    best_match_index = i
                    break

            if best_match:
                style['custom_curve_id'] = best_match.id
                remaining_curves.pop(best_match_index)

            yield test_id, x, y, style

        for curve, curve_data in custom_curves:
            values = curve_data.get('values')
            if not values:
                continue

            try:
                x_values, y_values = zip(*values)
            except ValueError:
                continue

            style = GraphConstants.DEFAULT_STYLE.copy()
            style['name'] = curve_data.get('name', f"Custom Curve {curve.id}")
            if 'color' in curve_data:
                style['color'] = curve_data['color']
            if 'line_width' in curve_data:
                style['width'] = curve_data['line_width']
            style['custom_curve_id'] = curve.id

            yield None, x_values, y_values, style

    def register_curve(self, test_id: int, curve: CurveItem):
        """Регистрация связи test_id -> curve"""
        self.curve_map[test_id] = curve

    def get_test_id_for_curve(self, curve: CurveItem) -> Optional['TestNode']:
        """Получение test_node по кривой"""
        for test_id, registered_curve in self.curve_map.items():
            if registered_curve == curve:
                return int(self.test_nodes.get(test_id)._data.id)
        return None

    def get_curves_for_test(self, test_id: int) -> List[CurveItem]:
        """Получение всех кривых для test_id"""
        return [curve for tid, curve in self.curve_map.items() if tid == test_id]

    def save_approximation(self, test_id, name, degree, color=None, line_width=None):
        """Сохраняет аппроксимированную кривую в БД
        
        Args:
            test_id: ID теста
            name: Название кривой
            degree: Степень полинома
            color: Цвет линии
            line_width: Толщина линии
            
        Returns:
            int: ID созданной кривой
        """
        values = {
            "name": name,
            "type": "polynomial",
            "test_id": test_id,
            "degree": degree
        }

        # Добавляем параметры стиля, если они указаны
        if color:
            values["color"] = color
        if line_width is not None:
            values["line_width"] = line_width

        custom_curve = self.data_manager.save_approximation(test_id, name, degree, values)

        # Обновляем кеш
        if custom_curve:
            self.other_data.append(custom_curve)

        return custom_curve.id if custom_curve else None

    def save_interpolation(self, test_id, name, interp_type, color=None, line_width=None):
        """Сохраняет интерполированную кривую в БД

        Args:
            test_id: ID теста
            name: Название кривой
            interp_type: Тип интерполяции
            color: Цвет линии
            line_width: Толщина линии
            
        Returns:
            int: ID созданной кривой
        """
        values = {
            "name": name,
            "type": interp_type,
            "test_id": test_id
        }

        # Добавляем параметры стиля, если они указаны
        if color:
            values["color"] = color
        if line_width is not None:
            values["line_width"] = line_width

        custom_curve = self.data_manager.save_interpolation(test_id, name, interp_type, values)

        # Обновляем кеш
        if custom_curve:
            self.other_data.append(custom_curve)

        return custom_curve.id if custom_curve else None

    def save_custom_curve(self, name: str, values) -> Optional[object]:
        """Сохраняет произвольную пользовательскую кривую"""

        curve_data = {
            "name": name or "",
            "values": [[float(point[0]), float(point[1])] for point in values]
        }

        custom_curve = self.data_manager.save_custom_curve(curve_data)

        if custom_curve:
            self.other_data.append(custom_curve)

        return custom_curve

    def remove_curve(self, curve_id):
        """Удаляет кастомную кривую по ID

        Args:
            curve_id: ID кривой
            
        Returns:
            bool: True если удаление успешно, False в противном случае
        """
        result = self.data_manager.remove_custom_curve(curve_id)

        # Если удаление успешно, обновляем кеш
        if result:
            self.remove_curve_from_cache(curve_id)

        return result

    def remove_curve_from_cache(self, curve_id):
        """Удаляет кривую из кеша
        
        Args:
            curve_id: ID кривой для удаления
        """
        # Удаляем кривую из other_data
        self.other_data = [curve for curve in self.other_data if curve.id != curve_id]
