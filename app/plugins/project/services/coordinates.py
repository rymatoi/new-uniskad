# services/coordinates.py
from collections import defaultdict
from itertools import groupby
import json

import numpy as np

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
        """Обрабатывает данные дополнительных кривых и аппроксимаций."""

        prepared_tests = {}
        for test_id, values in plot_data.items():
            try:
                x_values, y_values = zip(
                    *[(ItemProcessor.get_point_value(x), ItemProcessor.get_point_value(y))
                      for x, y in values]
                )
            except (InvalidCurveDataError, ValueError):
                continue

            if not (x_values and y_values):
                continue

            prepared_tests[test_id] = (
                x_values,
                y_values,
                TestProcessor.get_item_style(test_nodes[test_id])
            )

        for curve in other_data:
            try:
                curve_data = json.loads(curve.values) if isinstance(curve.values, str) else curve.values
            except json.JSONDecodeError:
                continue

            if not isinstance(curve_data, dict):
                continue

            curve_name = curve_data.get('name', f'Curve_{curve.id}')
            test_id = curve_data.get('test_id')

            base_style = GraphConstants.DEFAULT_STYLE.copy()
            custom_id = getattr(curve, 'id', None)

            if test_id in prepared_tests:
                x_base, y_base, test_style = prepared_tests[test_id]

                # Определяем источник данных для кривой
                if curve_data.get('values'):
                    try:
                        points = [
                            (ItemProcessor.get_point_value(pt[0]), ItemProcessor.get_point_value(pt[1]))
                            for pt in curve_data['values']
                        ]
                    except (InvalidPointValueError, ValueError, TypeError):
                        continue
                    if not points:
                        continue
                    x_new, y_new = zip(*points)
                    style = test_style.copy()
                elif 'degree' in curve_data:
                    degree = int(curve_data['degree'])
                    x_new, y_new = ApproximationService.polynomial_fit(x_base, y_base, degree)
                    style = GraphConstants.APPROXIMATION_STYLE.copy()
                    style['degree'] = degree
                    style['type'] = curve_data.get('type', 'polynomial')
                else:
                    curve_type = curve_data.get('type', 'quadratic')
                    x_new, y_new = Interpolation.quadratic_interpolation(x_base, y_base, kind=curve_type)
                    style = GraphConstants.INTERPOLATION_STYLE.copy()
                    style['type'] = curve_type

                # Применяем пользовательские параметры стиля
                if 'color' in curve_data:
                    style['color'] = curve_data['color']
                elif 'fill_color' in test_style:
                    style['color'] = test_style['fill_color']

                if 'line_width' in curve_data:
                    style['width'] = curve_data['line_width']

                style['name'] = curve_name
                if custom_id is not None:
                    style['custom_curve_id'] = custom_id

                yield test_id, list(x_new), list(y_new), style
            else:
                values = curve_data.get('values')
                if not values:
                    continue

                try:
                    points = [
                        (ItemProcessor.get_point_value(pt[0]), ItemProcessor.get_point_value(pt[1]))
                        for pt in values
                    ]
                except (InvalidPointValueError, ValueError, TypeError):
                    continue

                if not points:
                    continue

                x_new, y_new = zip(*points)
                style = base_style.copy()
                style['name'] = curve_name
                if 'color' in curve_data:
                    style['color'] = curve_data['color']
                if 'line_width' in curve_data:
                    style['width'] = curve_data['line_width']
                if custom_id is not None:
                    style['custom_curve_id'] = custom_id

                yield None, list(x_new), list(y_new), style

    @staticmethod
    def get_epure_data(plot_data, test_nodes):
        for test_id, values in plot_data.items():
            # Получаем и модифицируем стиль
            style = TestProcessor.get_item_style(test_nodes[test_id])
            style = style.copy()
            style['test_id'] = test_id
            scatter_values = []
            curve_values = []
            # Группируем и обрабатываем данные за один проход
            for _, group in groupby(values, key=lambda x: x[0]):
                y_values = None
                x_values = None
                curve_segment = None
                try:
                    y_values = np.fromiter(
                        (ItemProcessor.get_point_value(item[1]) for item in group),
                        dtype=float
                    )

                    if y_values.size == 0:
                        raise InvalidCurveDataError("Empty group")

                    x_values = np.arange(1, y_values.size + 1, dtype=float)

                    if y_values.size < GraphConstants.EPURE_DIRECT_DRAW_THRESHOLD:
                        curve_segment = (y_values, x_values)
                    else:
                        num_points = ItemProcessor._calculate_epure_point_count(y_values.size)
                        i_x, i_y = Interpolation.quadratic_interpolation(
                            x_values,
                            y_values,
                            num_points=num_points
                        )
                        curve_segment = (i_y, i_x)

                except (InvalidCurveDataError, ValueError, IndexError) as e:
                    print(f'Не удалось построить эпюру для испытания №{test_id}: {str(e)}')

                if curve_segment is not None and y_values is not None and x_values is not None:
                    scatter_values.append((y_values, x_values))
                    curve_values.append(curve_segment)
            if scatter_values and curve_values:
                yield test_id, scatter_values, curve_values, style

    @staticmethod
    def _calculate_epure_point_count(point_count: int) -> int:
        """Определяет количество точек интерполяции для эпюры."""
        if point_count <= 0:
            return 0

        points = int(point_count * GraphConstants.EPURE_INTERPOLATION_MULTIPLIER)
        points = max(points, GraphConstants.EPURE_INTERPOLATION_MIN_POINTS)
        points = min(points, GraphConstants.EPURE_INTERPOLATION_MAX_POINTS)

        # Гарантируем минимум две точки для корректного построения кривой
        return max(points, 2)

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
