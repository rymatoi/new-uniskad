# services/coordinates.py
from collections import defaultdict
from itertools import groupby
import json

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.core.exceptions import InvalidCurveDataError, InvalidPointValueError
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.services.interpolation import Interpolation
from app.plugins.project.utils.converters.graph_converter import GraphConverter
from app.plugins.project.services.approximation import ApproximationService


class ItemProcessor:
    @staticmethod
    def get_plot_data(plot_data, test_nodes):
        for test_id, values in plot_data.items():
            try:
                x, y = zip(
                    *[(ItemProcessor.get_point_value(x), ItemProcessor.get_point_value(y)) for x, y in
                      values])
                style = TestProcessor.get_item_style(test_nodes[test_id])
                if x and y:
                    yield test_id, x, y, style
            except InvalidCurveDataError:
                # print(f'Не удалось построить кривую для испытания №{test_id}')
                continue  # надо сообщать о некорректных кривых

    @staticmethod
    def get_other_data(plot_data, other_data, test_nodes):
        """
        Обрабатывает данные аппроксимаций и интерполяций.
        
        Args:
            plot_data: Данные исходных кривых
            other_data: Данные аппроксимаций/интерполяций в формате CustomCurve objects
                где values содержит JSON строку: {"name": "Испытание \"a\"", "type": "cubic", "test_id": 3214}
            test_nodes: Узлы тестов для получения стилей
        """
        for test_id, values in plot_data.items():
            try:
                # Получаем исходные координаты
                x, y = zip(
                    *[(ItemProcessor.get_point_value(x), ItemProcessor.get_point_value(y)) 
                      for x, y in values]
                )
                
                # Получаем базовый стиль из test_nodes
                base_style = TestProcessor.get_item_style(test_nodes[test_id])
                
                if not (x and y):
                    continue

                # Обрабатываем каждую дополнительную кривую для текущего теста
                for curve in other_data:
                    # Парсим JSON из строки values
                    curve_data = json.loads(curve.values)
                    
                    if curve_data['test_id'] == test_id:
                        curve_type = curve_data['type']
                        curve_name = curve_data['name']
                        
                        # Определяем тип кривой и применяем соответствующее преобразование
                        if 'degree' in curve_data:  # Аппроксимация
                            degree = int(curve_data['degree'])
                            x_new, y_new = ApproximationService.polynomial_fit(x, y, degree)
                            style = GraphConstants.APPROXIMATION_STYLE.copy()
                            # Добавляем степень для точного сопоставления
                            style['degree'] = degree
                        else:  # Интерполяция
                            x_new, y_new = Interpolation.quadratic_interpolation(x, y, kind=curve_type)
                            style = GraphConstants.INTERPOLATION_STYLE.copy()
                        
                        # Добавляем тип для точного сопоставления
                        style['type'] = curve_type
                        
                        # Используем пользовательские настройки стиля, если они есть
                        if 'color' in curve_data:
                            style['color'] = curve_data['color']
                        elif 'fill_color' in base_style:
                            style['color'] = base_style['fill_color']
                            
                        if 'line_width' in curve_data:
                            style['width'] = curve_data['line_width']
                            
                        style['name'] = curve_name
                        
                        yield test_id, x_new, y_new, style

            except (InvalidCurveDataError, json.JSONDecodeError):
                continue

    @staticmethod
    def get_epure_data(plot_data, test_nodes):
        for test_id, values in plot_data.items():
            # Получаем и модифицируем стиль
            style = TestProcessor.get_item_style(test_nodes[test_id])
            scatter_values = []
            curve_values = []
            # Группируем и обрабатываем данные за один проход
            for _, group in groupby(values, key=lambda x: x[0]):
                try:
                    # Создаем список точек с индексом и сразу извлекаем значения
                    points = [
                        (idx + 1, ItemProcessor.get_point_value(item[1]))
                        for idx, item in enumerate(group)
                    ]

                    if not points:
                        raise InvalidCurveDataError("Empty group")

                    # Разделяем координаты
                    x, y = zip(*points)

                    i_x, i_y = Interpolation.quadratic_interpolation(x, y, 1000)

                    scatter_values.append((y, x))
                    curve_values.append((i_y, i_x))

                except (InvalidCurveDataError, ValueError, IndexError) as e:
                    print(f'Не удалось построить эпюру для испытания №{test_id}: {str(e)}')
            if scatter_values and curve_values:
                yield scatter_values, curve_values, style

    @staticmethod
    def get_item_id(item):
        return item._data.project_id

    @staticmethod
    def get_x_param(item):
        return item.graph_label_x

    @staticmethod
    def get_y_param(item):
        return item.graph_label_y

    @staticmethod
    def get_point_value(point):
        if hasattr(point, 'prop_value'):
            return GraphConverter.str_to_float(point.prop_value)
        elif isinstance(point, str):
            return GraphConverter.str_to_float(point)
        elif isinstance(point, int) or isinstance(point, float):
            return point
        else:
            raise InvalidPointValueError
