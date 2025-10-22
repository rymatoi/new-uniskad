from typing import Iterable

from app.plugins.project.utils.converters.excel_converter import ExcelConverter


class ExcelDataHandler:
    @staticmethod
    def parse_clipboard_data(data):
        """Парсинг данных из буфера обмена Excel"""
        parsed_data = [line.split('\t') for line in data.split('\n') if line]
        curve_name = parsed_data[0][0]
        num_points = int(parsed_data[1][0])
        x_values = [float(ExcelConverter.excel_to_float(pair[0])) for pair in parsed_data[2:num_points + 2]]
        y_values = [float(ExcelConverter.excel_to_float(pair[1])) for pair in parsed_data[2:num_points + 2]]
        values = [(x_values[i], y_values[i]) for i
                  in range(len(x_values))]

        return curve_name, values

    @staticmethod
    def prepare_for_export(curve_name: str, x_values: Iterable, y_values: Iterable) -> str:
        """Форматирование данных для экспорта в Excel"""

        if x_values is None or y_values is None:
            return ""

        x_list = list(x_values)
        y_list = list(y_values)

        if len(x_list) != len(y_list):
            raise ValueError("Длины массивов X и Y должны совпадать")

        header_lines = [curve_name or "", str(len(x_list))]

        data_lines = [
            "\t".join((
                ExcelConverter.float_to_excel(x_list[i]),
                ExcelConverter.float_to_excel(y_list[i])
            ))
            for i in range(len(x_list))
        ]

        return "\n".join(header_lines + data_lines)
