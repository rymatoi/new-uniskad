import numpy as np
from numpy.polynomial import Polynomial


class ExtrapolationService:
    @staticmethod
    def polynomial_extrapolation(x, y, left_points: int, right_points: int, degree: int = 2):
        """
        Выполняет экстраполяцию данных с помощью полиномиальной аппроксимации.

        Args:
            x (array-like): Исходные x координаты
            y (array-like): Исходные y координаты
            left_points (int): Количество точек для экстраполяции влево
            right_points (int): Количество точек для экстраполяции вправо
            degree (int): Степень полинома

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
        if np.isclose(x_step, 0.0):
            x_step = 1.0

        left_points = max(0, int(left_points))
        right_points = max(0, int(right_points))

        if left_points > 0:
            x_left = x_sorted[0] - x_step * np.arange(left_points, 0, -1, dtype=float)
        else:
            x_left = np.array([], dtype=float)

        if right_points > 0:
            x_right = x_sorted[-1] + x_step * np.arange(1, right_points + 1, dtype=float)
        else:
            x_right = np.array([], dtype=float)

        x_extrap = np.concatenate((x_left, x_sorted, x_right))
        y_extrap = polynomial(x_extrap)

        return x_extrap, y_extrap
