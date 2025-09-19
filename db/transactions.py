import os.path
import time
from copy import copy
from datetime import datetime, timedelta

import openpyxl
import pandas as pd
from openpyxl.reader.excel import load_workbook
from openpyxl.utils import get_column_letter
from psycopg2 import DatabaseError

from app import basic_funcs
from app.basic_funcs import rgetattr, xls2xlsx_
from db import session, sp
from db.tables import PRODUCT


def import_file_data(product_name, file, up_node_id):
    def get_cells_for_import(filename, excel_id, worksheet=None) -> list:
        wb = xls2xlsx_(filename)
        ws = wb[worksheet] if worksheet else wb.active

        # Загружаем данные в pandas DataFrame
        data = pd.DataFrame([[cell.value for cell in row] for row in ws.iter_rows()])
        data = data.dropna(how='all', axis=1)  # Убираем полностью пустые столбцы
        data = data.dropna(how='all', axis=0)  # Убираем полностью пустые строки

        # Проверяем и корректируем индексацию
        row_names = data.iloc[:, 0].dropna().astype(str).values  # Первая колонка — имена строк
        rows = data.iloc[:, 1:]  # Убираем первую колонку, она уже обработана
        non_empty_columns = list(range(rows.shape[1]))  # Все оставшиеся столбцы (от 0 до n-1)

        # Получаем IDs параметров
        param_ids = sp.add_upd_sprav_names_array(row_names.tolist())

        # Дата для столбцов с уникальностью
        curr_date = datetime.now()
        date_column_dict = {
            i: curr_date + timedelta(milliseconds=i) for i in non_empty_columns
        }  # Уникальное время для каждого столбца

        # Формируем результаты для вставки
        result_columns = [
            (0, excel_id, 0, 'type', date_column_dict[i], None, None, 'column', False, 0, None)
            for i in non_empty_columns
        ]
        result_columns += [
            (0, excel_id, 0, 'column_npp', date_column_dict[i], None, None, f'{i}', False, 0, None)
            for i in non_empty_columns
        ]

        result_rows = [
            (0, excel_id, 0, 'type', None, None, None, 'row', False, 0, param_ids[i])
            for i, name in enumerate(row_names)
        ]
        result_rows += [
            (0, excel_id, 0, 'row_npp', None, None, None, str(i), False, 0, param_ids[i])
            for i, name in enumerate(row_names)
        ]

        # Формируем данные для ячеек
        props_to_take = {
            'value': 'value',
            'bold': 'font.b',
            'size': 'font.sz',
        }

        # Преобразование всех данных через генераторы
        def process_cells():
            for i, name in enumerate(row_names):
                for j, cell_value in enumerate(rows.iloc[i]):
                    if pd.isna(cell_value):
                        continue
                    for prop, prop_attr in props_to_take.items():
                        attr_val = cell_value  # Замените, если нужен доступ к реальным свойствам
                        if prop == 'value':
                            pass  # Дополнительная логика, если нужно
                        if attr_val is not None:
                            yield (
                                0, excel_id, 0, prop,
                                date_column_dict[j],  # Уникальная дата из date_column_dict
                                None, None, str(attr_val), False, 0, param_ids[i]
                            )
                    yield (
                        0, excel_id, 0, 'accuracy',
                        date_column_dict[j],  # Уникальная дата из date_column_dict
                        None, None, '2', False, 0, param_ids[i]
                    )
                    yield (
                        0, excel_id, 0, 'type',
                        date_column_dict[j],  # Уникальная дата из date_column_dict
                        None, None, 'cell', False, 0, param_ids[i]
                    )

        result_cells = list(process_cells())

        return result_cells + result_rows + result_columns

    # TODO нужно ли проверять отдельно каждую функцию?
    product = (None, None, up_node_id, 5, 'name', product_name, None, 0, None)
    new_product = sp.new_update_product_from_record(product)
    version = copy(new_product)
    version.prod_prop = 'final_version'
    version.prod_prop_value = '0'
    version = sp.new_update_product_from_record(version.table_fit(PRODUCT))
    datafile = sp.new_uniskad_datafile(int(new_product.id), 'input_excel', product_name[:30], file, "")
    with open(file, 'rb') as f:
        sp.new_uniskad_binfile(datafile.id_datafile, datafile.full_name, 'xlsx',
                               '',
                               '', f.read())
    sp.create_update_import_file_state(datafile.id_datafile, 10, 0)
    sp.new_excel_data_array(get_cells_for_import(datafile.full_name, datafile.id_datafile))
    return new_product, version


# @session.transaction
def import_other_file_data(filename, file, file_type, up_node_id):
    # TODO нужно ли проверять отдельно каждую функцию?
    product = (None, None, up_node_id, file_type, 'name', filename, None, 0, None)
    new_product = sp.new_update_product_from_record(product)
    new_product.type_ = 'file'
    datafile = sp.new_uniskad_datafile(int(new_product.id), 'other', filename, file, "")
    with open(file, 'rb') as f:
        sp.new_uniskad_binfile(datafile.id_datafile, datafile.full_name, 'other',
                               '',
                               '', f.read())
    return new_product


# @session.transaction
def import_project_other_file_data(filename, file, file_type, up_node_id):
    # TODO нужно ли проверять отдельно каждую функцию?
    product = (None, None, up_node_id, file_type, 'name', filename, None, None, None, 0, None)
    new_product = sp.new_update_project_from_record(product)
    new_product.type_ = 'file'
    datafile = sp.new_uniskad_datafile_project(int(new_product.id), 'other', filename, file, "")
    with open(file, 'rb') as f:
        sp.new_uniskad_binfile(datafile.id_datafile, datafile.full_name, 'pdf',
                               '',
                               '', f.read())
    return new_product


# @session.transaction
def delete_file_data(product_id, file_type, other_format=False):
    datafile = sp.get_product_uniskad_files(product_id, file_type)
    if not other_format:
        sp.remove_import_file_data(datafile.id_datafile)
        sp.remove_import_file_state(datafile.id_datafile)
    sp.remove_uniskad_datafiles_binary(datafile.id_datafile)
    sp.remove_uniskad_datafiles(datafile.id_datafile)
    sp.delete_product(product_id, True, True, True)
    return True


# @session.transaction
def delete_file_data_project(product_id, file_type, other_format=False):
    datafile = sp.get_project_uniskad_files(product_id, file_type)
    sp.remove_uniskad_datafiles_binary(datafile.id_datafile)
    sp.remove_uniskad_datafiles(datafile.id_datafile)
    sp.delete_project(product_id, True, True, True)
    return True
