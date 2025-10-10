from app.plugins.project.data.datamanagers.graph_datamanager import GraphDataManager
from app.plugins.project.services.coordinates import ItemProcessor
from app.plugins.project.services.data_processors.base_dp import DataProcessor
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.utils.collectors import PlotDataCollector as Collector
from typing import Dict, List, Optional
from app.plugins.project.visualization.widgets.curve import CurveItem


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
        """Получение данных для кривых"""
        curves_data = ItemProcessor.get_other_data(self.plot_data, self.other_data, self.test_nodes)

        for test_id, x, y, style in curves_data:
            yield test_id, x, y, style

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

    def save_custom_curve(self, name: str, points):
        """Сохраняет произвольную пользовательскую кривую."""
        curve_data = {
            "name": name,
            "values": [(float(x), float(y)) for x, y in points]
        }

        custom_curve = self.data_manager.save_custom_curve(curve_data)

        if custom_curve:
            self.other_data.append(custom_curve)

        return custom_curve
