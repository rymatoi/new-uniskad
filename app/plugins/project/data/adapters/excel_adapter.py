from app.plugins.project.utils.converters.graph_converter import excel_to_float


class ExcelDataHandler:
    @staticmethod
    def parse_clipboard_data(data):
        """Парсинг данных из буфера обмена Excel"""
        parsed_data = [line.split('\t') for line in data.split('\n') if line]
        curve_name = parsed_data[0][0]
        num_points = int(parsed_data[1][0])
        x_values = [float(excel_to_float(pair[0])) for pair in parsed_data[2:num_points + 2]]
        y_values = [float(excel_to_float(pair[1])) for pair in parsed_data[2:num_points + 2]]
        values = [(x_values[i], y_values[i]) for i
                  in range(len(x_values))]

        return curve_name, values

    @staticmethod
    def prepare_for_export(curve_data):
        """Форматирование данных для экспорта в Excel"""
