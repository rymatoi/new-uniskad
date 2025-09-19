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
        # Строим полином для экстраполяции
        polynomial = Polynomial.fit(x=x, y=y, deg=degree)

        # Создаем точки для экстраполяции
        x_step = (max(x) - min(x)) / len(x)
            
        # Создаем массивы точек для всех участков
        x_left = np.linspace(min(x) - left_points * x_step, min(x), left_points)
        x_middle = x  # исходные точки
        x_right = np.linspace(max(x), max(x) + right_points * x_step, right_points)
            
        # Объединяем все точки в один массив
        x_extrap = np.concatenate([x_left, x_middle, x_right])
        y_extrap = polynomial(x_extrap)

        return x_extrap, y_extrap 