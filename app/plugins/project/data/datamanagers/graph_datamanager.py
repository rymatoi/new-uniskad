import json
from typing import Optional

from app.plugins.project.utils.collectors import PlotDataCollector as Collector
from db import sp  # предположим, что это модуль работы с БД


class GraphDataManager:
    def __init__(self, project_id):
        self.project_id = project_id

    def load_curve_data(self, test_ids, param):
        """Получение данных кривых из БД"""
        return Collector.collect_cell_values(sp.get_x_curves(
            self.project_id,
            test_ids,
            param
        ))

    def load_custom_curves(self):
        """Получение данных кривых из БД"""
        return sp.get_custom_curves(self.project_id)

    def load_curve_data_array(self, test_ids, params):
        """Получение данных кривых из БД"""
        return Collector.collect_cell_values(sp.get_x_curves_array(
            self.project_id,
            test_ids,
            params
        ))

    def save_approximation(self, test_id: int, name: str, degree: int, values=None) -> Optional[object]:
        """
        Сохраняет аппроксимацию в базу данных

        Args:
            test_id: ID теста
            name: Название кривой
            degree: Степень полинома
            values: Предварительно подготовленные значения с параметрами стиля
        """
        try:
            if values:
                curve_data = values
            else:
                curve_data = {
                    "name": name,
                    "type": "polynomial",
                    "test_id": test_id,
                    "degree": degree
                }

            return self.save_custom_curve(curve_data)

        except Exception as e:
            print(f"Ошибка при сохранении аппроксимации: {str(e)}")
            return None

    def save_interpolation(self, test_id: int, name: str, interp_type: str = 'cubic', values=None) -> Optional[object]:
        """
        Сохраняет интерполяцию в базу данных

        Args:
            test_id: ID теста
            name: Название кривой
            interp_type: Тип интерполяции ('cubic' или 'quadratic')
            values: Предварительно подготовленные значения с параметрами стиля
        """
        try:
            if values:
                curve_data = values
            else:
                curve_data = {
                    "name": name,
                    "type": interp_type,
                    "test_id": test_id
                }

            return self.save_custom_curve(curve_data)

        except Exception as e:
            print(f"Ошибка при сохранении интерполяции: {str(e)}")
            return None

    def save_extrapolation(
            self,
            test_id: int,
            name: str,
            degree: int,
            left_points: int,
            right_points: int,
            *,
            left_limit: Optional[float] = None,
            right_limit: Optional[float] = None,
            values=None,
    ) -> Optional[object]:
        """Сохраняет экстраполяцию в базу данных"""

        try:
            if values:
                curve_data = values
            else:
                curve_data = {
                    "name": name,
                    "type": "extrapolation",
                    "test_id": test_id,
                    "degree": degree,
                    "left_points": left_points,
                    "right_points": right_points,
                }

                if left_limit is not None:
                    curve_data["left_limit"] = left_limit
                if right_limit is not None:
                    curve_data["right_limit"] = right_limit

            return self.save_custom_curve(curve_data)

        except Exception as e:
            print(f"Ошибка при сохранении экстраполяции: {str(e)}")
            return None

    def save_custom_curve(self, curve_data):
        """Сохранение пользовательской кривой"""
        return sp.new_upd_custom_curve(
            (None, self.project_id, json.dumps(curve_data))
        )

    def remove_custom_curve(self, curve_id):
        """Удаление пользовательской кривой"""
        return sp.remove_custom_curve(
            curve_id
        )
