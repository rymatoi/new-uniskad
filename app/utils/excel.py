import csv
import os.path

import xlrd
from xlrd.sheet import Cell
import xlsxwriter
from xlsxwriter import utility


def cell_value(cell: Cell):
    """Функция поления значения ячейки из файла Excel."""
    value = cell.value  # Получили значение
    if cell.ctype == xlrd.XL_CELL_DATE:  # Определем, тип ячейки время или иной
        value = xlrd.xldate_as_datetime(value, 0).strftime("%H:%M:%S")  # Формтируем значение под дату
    if isinstance(value, str) and value.isspace():
        return None
    return value


def csv_from_excel(excel_name: str):
    """Конвертирует файл excel в независимый формат csv."""
    if not (excel_name.endswith(".xlsx") or excel_name.endswith(".xls")):
        raise FileNotFoundError

    base_csv_name = os.path.splitext(os.path.basename(excel_name))[0]
    wb = xlrd.open_workbook(excel_name, formatting_info=True, ragged_rows=True)  # Открытие файла excel
    sheets = [sh for sh in wb.sheets() if sh.nrows > 0]
    add_sheet_name = len(sheets) > 1  # Количество непустых страниц больше одной

    for index, sheet in enumerate(sheets):  # Проходим по списку имен страниц файла excel
        csv_name = f'{base_csv_name}_{sheet.name}.csv' if add_sheet_name else f'{base_csv_name}.csv'
        with open(csv_name, 'w') as out:
            writer = csv.writer(out, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            for row in sheet.get_rows():
                writer.writerow([cell_value(cell) for cell in row])
            yield csv_name


def plot_to_xlsx(filepath, plot_name, label_x, label_y, curves):
    book_xlsx = xlsxwriter.Workbook(filepath)  # Создание файла эксель
    worksheet = book_xlsx.add_worksheet()  # Создание страницы в файле под значения точек
    chartsheet = book_xlsx.add_chartsheet()  # Создаем страницу в файле под графики точек
    x = label_x
    y = label_y
    curves = curves
    col_ = 0

    pie_chart = book_xlsx.add_chart({'type': 'scatter',  # Создаем графическую область в эксель,
                                     'subtype': 'straight'})  # которая состоит из точек, соединенные прямыми
    pie_chart.set_title({'name': plot_name})
    pie_chart.set_x_axis({'name': x})  # Выставляем подпись у оси Х
    pie_chart.set_y_axis({'name': y})  # Выставляем подпись у оси У
    pie_chart.set_legend({'position': 'bottom'})  # Указываем расположение подписей графиков

    for curve in curves:  # Проходимся по списку кривых
        worksheet.write(1, col_ * 2, x)  # Записываем в столбец имя параметра по оси Х
        worksheet.write(1, col_ * 2 + 1, y)  # Записываем в столбец имя параметра по оси У
        row_ = 2
        for p in curve.scatter.points():  # Проходимся по точкам графика и записываем их значения в столбцы
            worksheet.write(row_, col_ * 2, p.pos().x())
            worksheet.write(row_, col_ * 2 + 1, p.pos().y())
            row_ += 1

        # Определяем имя столбца, в диапазоне которого лежат нужные значения по оси Х и У
        lcol = xlsxwriter.utility.xl_col_to_name(col_ * 2)
        rcol = xlsxwriter.utility.xl_col_to_name(col_ * 2 + 1)

        if hasattr(curve, 'curve_name'):
            name = curve.curve_name if curve.curve_name else curve.curve.opts['name']
            worksheet.write(0, col_ * 2, name)
            pie_chart.add_series({  # Задаем параметры графика
                'name': name,  # имя кривой
                'categories': "=Sheet1!{0}3:{0}{1}".format(lcol, row_),  # Указываем диапазон Х, по которому строим
                'values': "=Sheet1!{0}3:{0}{1}".format(rcol, row_),  # Указываем диапазон У, по которому строим
                'marker': {'type': 'circle',
                           'border': {'color': curve.opts['pen'].color().name()},  # Выставляем цвет линии и точки
                           'fill': {'color': curve.opts['pen'].color().name()}},
                'line': {'color': curve.opts['pen'].color().name()}
            })

        col_ += 1

    chartsheet.set_chart(pie_chart)  # Указываем позицию, с которой надо выводить график
    chartsheet.activate()
    book_xlsx.close()
