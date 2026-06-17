# services/coordinates.py
from collections import defaultdict
from itertools import groupby
import json
import logging

import numpy as np

from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.core.exceptions import InvalidCurveDataError, InvalidPointValueError
from app.plugins.project.services.data_processors.test_dp import TestProcessor
from app.plugins.project.services.interpolation import Interpolation
from app.plugins.project.utils.converters.graph_converter import GraphConverter
from app.plugins.project.services.approximation import ApproximationService
from app.plugins.project.services.extrapolation import ExtrapolationService

logger = logging.getLogger(__name__)


class ItemProcessor:
    @staticmethod
    def get_custom_curve_test_id(curve_data, curve=None):
        """Return a normalized test id from curve JSON or a legacy model field."""
        raw_test_id = curve_data.get('test_id') if isinstance(curve_data, dict) else None
        if raw_test_id is None and curve is not None:
            raw_test_id = getattr(curve, 'test_id', None)
        if raw_test_id is None:
            return None
        try:
            return int(raw_test_id)
        except (TypeError, ValueError):
            return None

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
        Обрабатывает данные аппроксимаций, интерполяций и экстраполяций.
        
        Args:
            plot_data: Данные исходных кривых
            other_data: Данные аппроксимаций/интерполяций/экстраполяций в формате CustomCurve objects
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
                    try:
                        curve_data = json.loads(curve.values) if isinstance(curve.values, str) else curve.values
                    except (json.JSONDecodeError, TypeError):
                        logger.warning("Skipping custom curve %r: invalid JSON", getattr(curve, 'id', None))
                        continue
                    if not isinstance(curve_data, dict):
                        logger.warning("Skipping custom curve %r: values is not an object", getattr(curve, 'id', None))
                        continue

                    curve_test_id = ItemProcessor.get_custom_curve_test_id(curve_data, curve)
                    if curve_test_id is None:
                        logger.warning("Skipping custom curve %r: missing or invalid test_id", getattr(curve, 'id', None))
                        continue

                    if curve_test_id == int(test_id):
                        if not curve_data.get('type') or not curve_data.get('name'):
                            logger.warning("Skipping custom curve %r: missing required fields", getattr(curve, 'id', None))
                            continue
                        curve_type = curve_data['type']
                        curve_name = curve_data['name']

                        if curve_type == 'extrapolation':
                            degree = int(curve_data.get('degree', 2))
                            left_points = int(curve_data.get('left_points', 0))
                            right_points = int(curve_data.get('right_points', 0))
                            raw_left_limit = curve_data.get('left_limit')
                            raw_right_limit = curve_data.get('right_limit')

                            left_limit = None
                            if raw_left_limit is not None:
                                try:
                                    left_limit = float(raw_left_limit)
                                except (TypeError, ValueError):
                                    left_limit = None

                            right_limit = None
                            if raw_right_limit is not None:
                                try:
                                    right_limit = float(raw_right_limit)
                                except (TypeError, ValueError):
                                    right_limit = None

                            x_new, y_new = ExtrapolationService.polynomial_extrapolation(
                                x,
                                y,
                                left_points,
                                right_points,
                                degree,
                                left_limit=left_limit,
                                right_limit=right_limit,
                            )

                            style = GraphConstants.EXTRAPOLATION_STYLE.copy()
                            style['degree'] = degree
                            style['left_points'] = left_points
                            style['right_points'] = right_points
                            if left_limit is not None:
                                style['left_limit'] = left_limit
                            if right_limit is not None:
                                style['right_limit'] = right_limit

                        elif 'degree' in curve_data:  # Аппроксимация
                            degree = int(curve_data['degree'])
                            x_new, y_new = ApproximationService.polynomial_fit(x, y, degree)
                            style = GraphConstants.APPROXIMATION_STYLE.copy()
                            style['degree'] = degree

                        else:  # Интерполяция
                            x_new, y_new = Interpolation.quadratic_interpolation(x, y, kind=curve_type)
                            style = GraphConstants.INTERPOLATION_STYLE.copy()

                        style['type'] = curve_type

                        # Используем пользовательские настройки стиля, если они есть
                        if 'color' in curve_data:
                            style['color'] = curve_data['color']
                        elif 'fill_color' in base_style:
                            style['color'] = base_style['fill_color']

                        if 'line_width' in curve_data:
                            style['width'] = curve_data['line_width']

                        stored_style = curve_data.get('style')
                        if isinstance(stored_style, dict):
                            style.update(stored_style)

                        style['name'] = curve_name

                        yield test_id, x_new, y_new, style

            except (InvalidCurveDataError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                logger.warning("Skipping invalid custom curve data for test %r: %s", test_id, error)
                continue

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
                    raw_group = list(group)
                    numeric_values = []
                    for point_index, item in enumerate(raw_group):
                        raw_value = item[1] if len(item) > 1 else None
                        try:
                            numeric_values.append(ItemProcessor.get_point_value(raw_value))
                        except Exception as exc:
                            logger.warning(
                                'Skipping invalid epure point: test_id=%s, parameter=%s, point_index=%s, raw_value=%r, error=%r',
                                test_id, item[2] if len(item) > 2 else None, point_index, raw_value, exc, exc_info=True,
                            )
                    y_values = np.fromiter(numeric_values, dtype=float)

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

                except (InvalidCurveDataError, ValueError, IndexError) as exc:
                    logger.exception('Failed to build epure: test_id=%s, error=%r', test_id, exc)

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
        try:
            if hasattr(point, 'prop_value'):
                return GraphConverter.str_to_float(point.prop_value)
            elif isinstance(point, str):
                return GraphConverter.str_to_float(point)
            elif isinstance(point, int) or isinstance(point, float):
                return point
        except Exception as exc:
            logger.warning('Failed to convert point value to float: raw_value=%r, error=%r', point, exc, exc_info=True)
            raise
        logger.warning('Invalid point value type: raw_value=%r, type=%s', point, type(point).__name__)
        raise InvalidPointValueError
