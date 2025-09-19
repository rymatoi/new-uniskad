from scipy.interpolate import interp1d

import numpy as np
from scipy.interpolate import interp1d


class Interpolation:

    @staticmethod
    def quadratic_interpolation(x, y, num_points=1000, kind='quadratic'):
        """
        Выполняет квадратичную интерполяцию массивов x и y.

        Параметры:
        x, y (array-like): Исходные данные.
        num_points (int): Количество точек в интерполированном массиве.
        kind (str): Тип интерполяции ('quadratic', 'cubic', etc.)

        Возвращает:
        new_x, new_y (ndarray): Интерполированные массивы.
        """
        # Преобразуем в numpy массивы
        x = np.asarray(x)
        y = np.asarray(y)
        
        # Удаляем дубликаты по оси X
        # Находим уникальные x и индексы первого вхождения
        unique_x, unique_indices = np.unique(x, return_index=True)
        
        # Если были найдены дубликаты, оставляем только уникальные значения
        if len(unique_x) < len(x):
            print(f"Предупреждение: найдены дублирующиеся значения по оси X. {len(x) - len(unique_x)} дубликатов будут удалены.")
            x = x[unique_indices]
            y = y[unique_indices]
            
        # Сортировка данных
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]

        # Создание интерполяционной функции
        interp_func = interp1d(
            x_sorted,
            y_sorted,
            kind=kind,
            assume_sorted=True
        )

        # Генерация новых точек
        new_x = np.linspace(x_sorted.min(), x_sorted.max(), num_points)
        new_y = interp_func(new_x)

        return new_x, new_y