from typing import Optional

import numpy as np
from numpy.polynomial import Polynomial


class ExtrapolationService:
    """Сервис экстраполяции данных."""

    # Ограничение на число добавляемых точек с каждой стороны графика
    MAX_POINTS_PER_SIDE = 10000

    @staticmethod
    def polynomial_extrapolation(
            x,
            y,
            left_points: int,
            right_points: int,
            degree: int = 2,
            *,
            left_limit: Optional[float] = None,
            right_limit: Optional[float] = None,
    ):
        """Выполняет экстраполяцию данных с помощью полиномиальной аппроксимации.

        Args:
            x (array-like): Исходные x координаты
            y (array-like): Исходные y координаты
            left_points (int): Количество точек для экстраполяции влево
            right_points (int): Количество точек для экстраполяции вправо
            degree (int): Степень полинома
            left_limit (Optional[float]): Желаемая минимальная граница экстраполяции
            right_limit (Optional[float]): Желаемая максимальная граница экстраполяции

        Returns:
            tuple: (x_extrap, y_extrap) - экстраполированные координаты
        """
        x_values = np.asarray(x, dtype=float)
        y_values = np.asarray(y, dtype=float)

        if x_values.size == 0 or y_values.size == 0:
            return x_values, y_values

        sort_idx = np.argsort(x_values)
        x_sorted = x_values[sort_idx]
        y_sorted = y_values[sort_idx]

        effective_degree = min(int(degree), x_sorted.size - 1)
        if effective_degree < 1:
            return x_sorted, y_sorted

        polynomial = Polynomial.fit(x=x_sorted, y=y_sorted, deg=effective_degree)

        diffs = np.diff(x_sorted)
        valid_diffs = diffs[~np.isclose(diffs, 0.0)]
        x_step = float(np.median(valid_diffs)) if valid_diffs.size else 1.0
        if valid_diffs.size:
            unique_x = np.unique(x_sorted)
            if unique_x.size > 1:
                avg_step = float(np.ptp(unique_x)) / (unique_x.size - 1)
                if np.isfinite(avg_step) and avg_step > 0:
                    x_step = max(x_step, avg_step)
        if np.isclose(x_step, 0.0):
            x_step = 1.0

        min_step = max(x_step, np.finfo(float).eps)

        left_points = max(0, int(left_points))
        right_points = max(0, int(right_points))

        min_x = float(x_sorted[0])
        max_x = float(x_sorted[-1])

        left_span = None
        if left_limit is not None:
            left_span = max(0.0, min_x - float(left_limit))
            if left_span > 0:
                required_left = int(np.ceil(left_span / min_step))
                left_points = max(left_points, required_left)
        if left_span is None and left_points > 0:
            left_span = min_step * left_points

        right_span = None
        if right_limit is not None:
            right_span = max(0.0, float(right_limit) - max_x)
            if right_span > 0:
                required_right = int(np.ceil(right_span / min_step))
                right_points = max(right_points, required_right)
        if right_span is None and right_points > 0:
            right_span = min_step * right_points

        left_points = min(left_points, ExtrapolationService.MAX_POINTS_PER_SIDE)
        right_points = min(right_points, ExtrapolationService.MAX_POINTS_PER_SIDE)

        if left_points > 0 and (left_span is None or left_span == 0.0):
            left_span = min_step * left_points
        if right_points > 0 and (right_span is None or right_span == 0.0):
            right_span = min_step * right_points

        if left_points > 0 and left_span and left_span > 0:
            left_step = left_span / left_points
            start_left = min_x - left_span
            end_left = min_x - left_step
            if end_left < start_left:
                end_left = start_left
            x_left = np.linspace(start_left, end_left, left_points, dtype=float)
        elif left_points > 0:
            x_left = min_x - min_step * np.arange(left_points, 0, -1, dtype=float)
        else:
            x_left = np.array([], dtype=float)

        if right_points > 0 and right_span and right_span > 0:
            right_step = right_span / right_points
            start_right = max_x + right_step
            end_right = max_x + right_span
            if end_right < start_right:
                end_right = start_right
            x_right = np.linspace(start_right, end_right, right_points, dtype=float)
        elif right_points > 0:
            x_right = max_x + min_step * np.arange(1, right_points + 1, dtype=float)
        else:
            x_right = np.array([], dtype=float)

        x_extrap = np.concatenate((x_left, x_sorted, x_right))
        y_extrap = polynomial(x_extrap)

        return x_extrap, y_extrap
