import numpy as np
from scipy.interpolate import interp1d


class Interpolation:

    @staticmethod
    def quadratic_interpolation(x, y, num_points=1000, kind='quadratic'):
        """Выполняет интерполяцию массивов ``x`` и ``y``."""
        x = np.asarray(x)
        y = np.asarray(y)

        num_points = max(int(num_points), 2)

        unique_x, unique_indices = np.unique(x, return_index=True)
        if len(unique_x) < len(x):
            print(
                f"Предупреждение: найдены дублирующиеся значения по оси X. "
                f"{len(x) - len(unique_x)} дубликатов будут удалены."
            )
            x = x[unique_indices]
            y = y[unique_indices]

        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]

        interp_func = interp1d(
            x_sorted,
            y_sorted,
            kind=kind,
            assume_sorted=True
        )

        new_x = np.linspace(x_sorted.min(), x_sorted.max(), num_points)
        new_y = interp_func(new_x)

        return new_x, new_y
