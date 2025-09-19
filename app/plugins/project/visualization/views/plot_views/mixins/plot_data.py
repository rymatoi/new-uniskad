from app.plugins.project.visualization.widgets.curve import CurveItem
from typing import Any, Union, List, Dict, Set, Callable
import numpy as np
import pyqtgraph as pg


class PlotDataMixin:
    """Миксин для управления данными графика"""

    # Внешние атрибуты и методы
    plotItem: Any
    item: Any
    DATA_PROCESSOR: Any
    addItem: Callable
    init_legend: Callable
    selected_points: dict
    _display_settings: dict
    main_window: Any
    constraints: dict
    param_constraints: list

    def __init__(self, item, main_window):
        self._curve_items: List[CurveItem] = []
        self._item = item
        self.data_processor: Any = self.init_data_processor()
        self.constraints = {}
        self.param_constraints = []

        self.selected_points = {}

        self.init_legend()
        self.set_main_window(main_window)

    @property
    def item(self):
        return self._item

    @property
    def curve_items(self):
        return self._curve_items

    def set_main_window(self, mw):
        """
        Установка ссылки на главное окно
        """
        self.main_window = mw

    def init_data_processor(self):
        if self.DATA_PROCESSOR is not None:
            return self.DATA_PROCESSOR(self.item)
        return None

    def add_curve(self, x: Union[list, np.ndarray],
                  y: Union[list, np.ndarray],
                  name: str = "Curve",
                  **style) -> CurveItem:
        curve = CurveItem(x, y, name=name, style=style)
        self.addItem(curve)
        self.curve_items.append(curve)
        self.selected_points[curve] = set()
        return curve

    def clear(self):
        self.plotItem.clear()
        self.plotItem.legend.clear()

    def prepare_curves(self):
        pass

    def commit_changes(self):
        pass

    def _apply_multipliers(self):
        x_mul = self._display_settings['x_multiplier']
        x_div = self._display_settings['x_divider']
        y_mul = self._display_settings['y_multiplier']
        y_div = self._display_settings['y_divider']

        for curve in self.curve_items:
            curve.apply_multipliers(x_mul, x_div, y_mul, y_div)

    def _refresh_curves(self):
        x_mul = float(self.item.graph_x_multiplier)
        x_div = float(self.item.graph_x_dultiplier)
        y_mul = float(self.item.graph_y_multiplier)
        y_div = float(self.item.graph_y_dultiplier)

        for curve in self.curve_items:
            if hasattr(curve, 'apply_multipliers'):
                curve.apply_multipliers(x_mul, x_div, y_mul, y_div)

    def remove_curve(self, curve) -> None:
        """Удаляет кривую с графика и из регистрации
        
        Args:
            curve: Объект кривой для удаления
        """
        if curve in self.itemList():
            self.removeItem(curve)
            # Удаляем связь из curve_map
            test_id = self.plot_processor.get_test_id_for_curve(curve)
            if test_id in self.plot_processor.curve_map:
                del self.plot_processor.curve_map[test_id]

    def remove_custom_curve(self, curve) -> bool:
        """Удаляет пользовательскую кривую из БД и с графика
        
        Args:
            curve: Объект кривой для удаления
            
        Returns:
            bool: True если удаление успешно, False в противном случае
        """
        # Получаем ID кастомной кривой
        if not hasattr(curve, 'custom_curve_id') or curve.custom_curve_id is None:
            return False
            
        # Удаляем из базы данных
        result = self.data_processor.remove_curve(curve.custom_curve_id)
        
        # Если удаление из БД успешно, удаляем с графика
        if result:
            # Удаляем из интерфейса
            self.removeItem(curve)
            
            # Удаляем из списка кривых
            if curve in self.curve_items:
                self.curve_items.remove(curve)
                
            # Удаляем из словаря выбранных точек
            if curve in self.selected_points:
                del self.selected_points[curve]
            
            # Обновляем легенду
            if hasattr(self.plotItem, 'legend') and self.plotItem.legend:
                for i, (sample, label) in enumerate(list(self.plotItem.legend.items)):
                    if getattr(sample, 'item', None) == curve:
                        self.plotItem.legend.items.pop(i)
                        sample.setParentItem(None)
                        label.setParentItem(None)
                        break
                        
            return True
            
        return False

    def check_x_val_constraint(self, i, project_id):
        """Проверяет, удовлетворяет ли значение ограничениям параметров"""
        params = self.param_constraints
        for param in params:
            if (project_id, param) in self.constraints.keys():
                if not self.constraints[(project_id, param)].is_valid(i):
                    return False
        return True

    def filter_by_constraints(self, x_data, y_data, test_id):
        """Фильтрует точки кривой по ограничениям параметров"""
        filtered_x = []
        filtered_y = []

        for i in range(len(x_data)):
            # Проверяем, что точка не None и удовлетворяет ограничениям
            if (x_data[i] is not None and y_data[i] is not None and
                    self.check_x_val_constraint(i, test_id)):
                filtered_x.append(x_data[i])
                filtered_y.append(y_data[i])

        return filtered_x, filtered_y

    def setup_constraint_data(self, constraints_data):
        """Настраивает ограничения по параметрам"""

        class ParamConstraint:
            def __init__(self, name, test_id, min_val, max_val):
                self.name = name
                self.test_id = test_id
                self.x_data = []
                self.min_val = min_val
                self.max_val = max_val
                self.cformula = False

            def is_valid(self, i):
                if i >= len(self.x_data):
                    return True
                if not self.x_data[i].replace('.', '', 1).isdigit():
                    return True
                if self.min_val <= float(self.x_data[i]) <= self.max_val:
                    return True
                return False

        self.constraints = {}
        import json
        constr = json.loads(self.item.graph_constraints)

        # constraints_data - это словарь вида {(param_name, project_id): [список ProjectData]}
        for key, data_list in constraints_data.items():
            param_name, project_id = key

            if (project_id, param_name) not in self.constraints.keys():
                cns = ParamConstraint(
                    name=param_name,
                    test_id=project_id,
                    min_val=constr[param_name]['min'],
                    max_val=constr[param_name]['max']
                )
                self.constraints[(project_id, param_name)] = cns

            cns = self.constraints[(project_id, param_name)]

            # Обрабатываем все объекты ProjectData для этого параметра/проекта
            for data in data_list:
                if data.param_prop_name == 'cformula':
                    if not cns.cformula:
                        cns.cformula = True
                        cns.x_data.clear()
                    cns.x_data.append(data.prop_value)
                elif data.param_prop_name == 'value' and not cns.cformula:
                    cns.x_data.append(data.prop_value)

    def filter_by_conditions(self, x_data, y_data, test_node):
        """
        Фильтрует точки по условиям третьего параметра.
        
        Args:
            x_data: массив X-координат
            y_data: массив Y-координат
            test_node: узел теста с условиями
            
        Returns:
            словарь {условие: (отфильтрованные x, y, стиль)}
        """
        import ast
        from app.plugins.project.utils.converters.graph_converter import GraphConverter

        def to_float(val):
            try:
                if val is None:
                    return None
                return float(val)
            except (ValueError, TypeError):
                return None

        def compare_floats(num1, num2):
            # Преобразуем числа в строки для определения количества знаков после запятой
            str_num1 = f"{num1:.10f}".rstrip('0').rstrip('.')
            str_num2 = f"{num2:.10f}".rstrip('0').rstrip('.')

            # Определяем количество знаков после запятой у каждого числа
            decimal_places1 = len(str_num1.split('.')[1]) if '.' in str_num1 else 0
            decimal_places2 = len(str_num2.split('.')[1]) if '.' in str_num2 else 0

            # Определяем минимальное количество знаков после запятой
            decimal_places = min(decimal_places1, decimal_places2)

            # Округляем числа до минимального количества знаков после запятой
            rounded_num1 = round(num1, decimal_places)
            rounded_num2 = round(num2, decimal_places)

            # Сравниваем округленные числа
            return rounded_num1 == rounded_num2

        # Результирующий словарь с группами точек
        result_groups = {}

        # Проверяем, есть ли условия
        if not (test_node.use_conditions == 'True' and test_node.conditions and test_node.conditions != '[]'):
            return result_groups

        # Парсим условия
        conditions = ast.literal_eval(test_node.conditions)
        if not conditions:
            return result_groups

        # Получаем параметр Z, по которому будем группировать
        z_param = conditions[0]['x']

        # Словарь для быстрого доступа к условиям по значению
        condition_dict = {to_float(c['val']): c for c in conditions}

        # Получаем данные по Z-параметру
        z_data = self.data_processor.data_manager.load_curve_data(
            [test_node._data.project_id],
            z_param
        )

        # Ключ для получения данных из словаря z_data
        z_key = (z_param, test_node._data.project_id)
        if z_key not in z_data:
            return result_groups

        # Собираем все значения параметра Z
        z_values = []
        for param_obj in z_data[z_key]:
            if param_obj.param_prop_name == 'value':
                z_values.append(param_obj.prop_value)

        # Если нет значений параметра Z, возвращаем пустой результат
        if not z_values:
            return result_groups

        # Для каждой точки
        for i in range(min(len(x_data), len(y_data), len(z_values))):
            # Пропускаем точки с пустыми значениями
            if x_data[i] is None or y_data[i] is None or z_values[i] is None:
                continue

            try:
                # Преобразуем значение Z в число
                z_val = GraphConverter.str_to_float(z_values[i])
            except Exception:
                continue

            # Ищем соответствующее условие
            for val, condition in condition_dict.items():
                if compare_floats(z_val, val):
                    # Создаем ключ для группы
                    condition_key = f"{condition['name']}_{condition['color']}_{condition['type']}"

                    # Если группа еще не создана - инициализируем
                    if condition_key not in result_groups:
                        result_groups[condition_key] = {
                            'x': [],
                            'y': [],
                            'style': {
                                'color': condition['color'],
                                'symbol': condition['type'],
                                'symbol_size': int(condition['point_size']),
                                'name': condition['name']
                            }
                        }

                    # Добавляем точку в соответствующую группу
                    result_groups[condition_key]['x'].append(x_data[i])
                    result_groups[condition_key]['y'].append(y_data[i])
                    break

        return result_groups
