from app.plugins.project.data.datamanagers.graph_datamanager import GraphDataManager
from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.base_dp import DataProcessor
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.utils.collectors import PlotDataCollector as Collector
from typing import Any, Dict, List, Optional, Tuple
from app.plugins.project.visualization.widgets.curve import CurveItem
from app.plugins.project.core.constants import GraphConstants
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
        """Получение данных для дополнительных кривых"""

        manual_curves: List[Tuple[Any, Dict[str, Any]]] = []
        approx_curves: List[Tuple[Any, Dict[str, Any]]] = []

        for curve in self.other_data:
            curve_values = json.loads(curve.values) if isinstance(curve.values, str) else curve.values
            if isinstance(curve_values, dict) and ('points' in curve_values or curve_values.get('type') == 'manual'):
                manual_curves.append((curve, curve_values))
            else:
                approx_curves.append((curve, curve_values))

        if approx_curves:
            approx_objects = [curve for curve, _ in approx_curves]
            curves_data = ItemProcessor.get_other_data(self.plot_data, approx_objects, self.test_nodes)

            remaining_curves = list(approx_curves)

            for test_id, x, y, style in curves_data:
                curve_name = style.get('name', '')
                curve_type = style.get('type', '')
                curve_degree = style.get('degree', None)

                best_match = None
                best_match_index = -1

                for i, (curve_obj, curve_data) in enumerate(remaining_curves):
                    if curve_data.get('test_id') != test_id or curve_data.get('name') != curve_name:
                        continue

                    curve_matches = True

                    if curve_type and 'type' in curve_data and curve_data.get('type') != curve_type:
                        curve_matches = False

                    if curve_degree is not None and 'degree' in curve_data and curve_data.get('degree') != curve_degree:
                        curve_matches = False

                    if curve_matches:
                        for field in ('left_points', 'right_points', 'left_limit', 'right_limit'):
                            if field in curve_data:
                                style_value = style.get(field)
                                if style_value is None:
                                    continue
                                if curve_data.get(field) != style_value:
                                    curve_matches = False
                                    break

                    if curve_matches:
                        best_match = curve_obj
                        best_match_index = i
                        break

                if best_match:
                    style['custom_curve_id'] = best_match.id
                    remaining_curves.pop(best_match_index)

                yield test_id, x, y, style

        for curve_obj, curve_data in manual_curves:
            points = curve_data.get('points') or []
            if not points:
                continue

            x_values: List[float] = []
            y_values: List[float] = []

            for point in points:
                if not isinstance(point, (list, tuple)) or len(point) < 2:
                    continue
                try:
                    x_val = float(point[0])
                    y_val = float(point[1])
                except (TypeError, ValueError):
                    continue
                x_values.append(x_val)
                y_values.append(y_val)

            if not x_values or not y_values:
                continue

            style = curve_data.get('style', {}).copy()
            base_style = GraphConstants.DEFAULT_STYLE.copy()
            base_style.update(style)
            base_style['name'] = curve_data.get('name', base_style.get('name', 'Кривая'))
            base_style['custom_curve_id'] = curve_obj.id

            yield curve_data.get('test_id'), x_values, y_values, base_style

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

    def save_extrapolation(
            self,
            test_id,
            name,
            degree,
            left_points,
            right_points,
            *,
            left_limit=None,
            right_limit=None,
            color=None,
            line_width=None,
    ):
        """Сохраняет экстраполированную кривую в БД"""

        if test_id is None:
            return None

        values = {
            "name": name,
            "type": "extrapolation",
            "test_id": test_id,
            "degree": degree,
            "left_points": left_points,
            "right_points": right_points,
        }

        if left_limit is not None:
            values["left_limit"] = left_limit
        if right_limit is not None:
            values["right_limit"] = right_limit
        if color:
            values["color"] = color
        if line_width is not None:
            values["line_width"] = line_width

        custom_curve = self.data_manager.save_extrapolation(
            test_id,
            name,
            degree,
            left_points,
            right_points,
            left_limit=left_limit,
            right_limit=right_limit,
            values=values,
        )

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

    def save_manual_curve(self, name: str, points: List[Tuple[float, float]], style: Dict[str, Any],
                          metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Сохраняет произвольную кривую (например, вставленную из буфера обмена)."""

        payload = {
            'name': name,
            'type': 'manual',
            'points': [[float(x), float(y)] for x, y in points],
            'style': style,
            'metadata': metadata or {},
        }

        custom_curve = self.data_manager.save_custom_curve(payload)

        if custom_curve:
            self.other_data.append(custom_curve)
            return custom_curve.id

        return None

