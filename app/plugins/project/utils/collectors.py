from collections import OrderedDict, defaultdict


class PlotDataCollector:
    @staticmethod
    def collect_cell_values(db_objects):
        operated = OrderedDict()
        broken_keys = []
        for o in db_objects:
            key = o.excel_param_name, o.date_time_izm, o.project_id
            if o.prop_name == 'broken' and o.prop_value == 'True':
                if key not in broken_keys:
                    broken_keys.append(key)
            elif o.prop_name == 'broken' and o.prop_value == 'False':
                if key in broken_keys:
                    broken_keys.remove(key)
            if o.prop_name == 'cformula':
                operated[key] = o
            elif o.prop_name == 'value':
                if key not in operated:
                    operated[key] = o

        result = {}
        for o in list(operated.values()):
            key = o.excel_param_name, o.project_id
            if key not in result:
                result[key] = []
            if (o.excel_param_name, o.date_time_izm, o.project_id) in broken_keys:
                o.prop_value = None
            result[key].append(o)

        return result

    @staticmethod
    def collect_epure_values(db_objects):
        _values_dict = defaultdict(list)
        for _v in db_objects:
            _values_dict[_v.project_id].append((_v.x_val, _v.y_val, _v.excel_param_name))

        # In-place сортировка для каждого списка
        for project_id in _values_dict:
            _values_dict[project_id].sort(key=lambda x: x[0])

        return _values_dict

    @staticmethod
    def process_plot_values(x_data, y_data, x_param, y_param):
        """Оптимизированная обработка данных для графиков"""
        x_data, y_data = PlotDataCollector.filter_common_keys(x_data, y_data)

        # Получаем все номера испытаний, которые есть как для x_param, так и для y_param
        x_trials = {key[1] for key in x_data.keys() if key[0] == x_param}
        y_trials = {key[1] for key in y_data.keys() if key[0] == y_param}

        return {
            trial: list(zip(x_data[(x_param, trial)], y_data[(y_param, trial)]))
            for trial in (x_trials & y_trials)
        }

    @staticmethod
    def filter_common_keys(x_data, y_data):
        # Извлекаем множества номеров испытаний из обоих словарей
        x_trials = {key[1] for key in x_data.keys()}
        y_trials = {key[1] for key in y_data.keys()}

        # Находим пересечение номеров испытаний
        common_trials = x_trials & y_trials

        # Фильтруем словари, оставляя только ключи с общими номерами испытаний
        filtered_x_data = {key: x_data[key] for key in x_data if key[1] in common_trials}
        filtered_y_data = {key: y_data[key] for key in y_data if key[1] in common_trials}

        return filtered_x_data, filtered_y_data
