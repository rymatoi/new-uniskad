from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.drawing.colors import ColorChoice
from openpyxl.chart.marker import Marker
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt

from openpyxl.chart.axis import ChartLines
from app.plugins.project.core.constants import GraphConstants


class PlotExcelExporter:
    """Класс для экспорта данных графика в Excel с сохранением стилей."""

    # Маппинг типов линий Qt в типы линий Excel
    LINE_STYLE_MAP = {
        Qt.NoPen: 'none',
        Qt.SolidLine: 'solid',
        Qt.DashLine: 'dash',
        Qt.DotLine: 'dot'
    }

    def __init__(self):
        self.wb = Workbook()
        # Создаем два листа: для данных и для графика
        self.ws_data = self.wb.active
        self.ws_data.title = "Данные"
        self.ws_plot = self.wb.create_sheet(title="График")
        self.current_row = 1
        self.data_ranges = []  # Для хранения диапазонов данных каждой кривой

    def export(self, plot_view, filename):
        """Экспортирует данные и график в Excel файл."""
        self._export_curves(plot_view)
        self._create_plot(plot_view)
        self.wb.save(filename)

    def _get_excel_color(self, qt_color):
        """Преобразует Qt цвет в формат Excel."""
        return f"{qt_color.red():02x}{qt_color.green():02x}{qt_color.blue():02x}"

    def _export_curves(self, plot_view):
        """Экспортирует данные кривых и сохраняет их диапазоны."""
        for curve in plot_view.curve_items:
            if not curve.isVisible():
                continue

            start_row = self.current_row

            # Получаем цвет и стиль кривой
            pen = curve.opts.get('pen')
            symbol_brush = curve.opts.get('symbolBrush')

            if symbol_brush and hasattr(symbol_brush, 'color'):
                color = symbol_brush.color()
            elif isinstance(pen, tuple):
                color = QColor(*pen)  # Если pen это кортеж (r,g,b), создаем QColor
            else:
                color = pen.color()

            rgb_color = self._get_excel_color(color)

            # Создаем стили
            title_fill = PatternFill(start_color=rgb_color, end_color=rgb_color, fill_type="solid")
            border = Border(left=Side(style='thin', color=rgb_color),
                            right=Side(style='thin', color=rgb_color),
                            top=Side(style='thin', color=rgb_color),
                            bottom=Side(style='thin', color=rgb_color))

            # Записываем название кривой
            self.ws_data.merge_cells(f'A{self.current_row}:D{self.current_row}')
            cell = self.ws_data.cell(row=self.current_row, column=1, value=curve.name())
            cell.fill = title_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal='left')

            # Заголовки столбцов
            self.current_row += 1
            headers = ['№ точки', 'X', 'Y', 'Статус']
            for col, header in enumerate(headers, 1):
                cell = self.ws_data.cell(row=self.current_row, column=col, value=header)
                cell.font = Font(bold=True)
                cell.border = border

            # Данные точек
            for i in range(len(curve.scatter.points())):
                self.current_row += 1
                x_data = curve.xData[i] if hasattr(curve, 'xData') else curve.scatter.points()[i].pos().x()
                y_data = curve.yData[i] if hasattr(curve, 'yData') else curve.scatter.points()[i].pos().y()
                status = "Выделена" if i in plot_view.selected_points[curve] else ""

                row_data = [i + 1, x_data, y_data, status]
                for col, value in enumerate(row_data, 1):
                    cell = self.ws_data.cell(row=self.current_row, column=col, value=value)
                    cell.border = border
                    if status and col == 4:
                        cell.font = Font(color="FF0000", bold=True)

            # Добавляем дополнительную информацию
            if hasattr(curve, 'get_point_info'):
                for i in range(len(curve.scatter.points())):
                    additional_info = curve.get_point_info(i)
                    if additional_info:
                        for key, value in additional_info.items():
                            self.current_row += 1
                            cell = self.ws_data.cell(row=self.current_row, column=1, value=key)
                            cell.font = Font(bold=True)
                            cell = self.ws_data.cell(row=self.current_row, column=2, value=str(value))

            # Сохраняем диапазон данных для построения графика
            end_row = self.current_row - 2  # Исключаем пустые строки
            self.data_ranges.append({
                'name': curve.name(),
                'x_range': f'Данные!$B${start_row + 2}:$B${end_row}',  # +2 для пропуска заголовков
                'y_range': f'Данные!$C${start_row + 2}:$C${end_row}',
                'color': rgb_color,
                'symbol': self._get_marker_style(curve),
                'selected_points': plot_view.selected_points.get(curve, set()),
                'visible': curve.isVisible()
            })

            # Пустая строка между кривыми
            self.current_row += 2

        # Автоподбор ширины столбцов
        for column in self.ws_data.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            self.ws_data.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width

    def _get_marker_style(self, curve):
        """Определяет стиль маркера точки для Excel."""
        # Для интерполированных кривых маркеры не нужны
        if not hasattr(curve, 'scatter'):
            return 'none'

        symbol_map = {
            'o': 'circle',
            's': 'square',
            't': 'triangle',
            'd': 'diamond',
            '+': 'plus',
            'x': 'x',
            'star': 'triangle',
            None: 'none'
        }
        symbol = curve._style_config.get('symbol')
        return symbol_map.get(symbol, 'none')

    def _create_plot(self, plot_view):
        """Создает график в Excel."""
        chart = ScatterChart()
        chart.title = None
        chart.x_axis.title = plot_view.plotItem.axes['bottom']['item'].label.toPlainText()
        chart.y_axis.title = plot_view.plotItem.axes['left']['item'].label.toPlainText()

        # Настраиваем сетку
        chart.x_axis.majorGridlines = ChartLines()
        chart.y_axis.majorGridlines = ChartLines()

        # Делаем сетку серой и тонкой
        chart.x_axis.majorGridlines.spPr = GraphicalProperties(
            ln=LineProperties(
                solidFill=ColorChoice(srgbClr="CCCCCC"),  # Светло-серый цвет
            )
        )
        chart.x_axis.majorGridlines.spPr.ln.w = int(0.5 * 9525)  # Тонкая линия

        chart.y_axis.majorGridlines.spPr = GraphicalProperties(
            ln=LineProperties(
                solidFill=ColorChoice(srgbClr="CCCCCC"),
            )
        )
        chart.y_axis.majorGridlines.spPr.ln.w = int(0.5 * 9525)

        for curve_data in self.data_ranges:
            if not curve_data['visible']:
                continue

            curve = next(c for c in plot_view.curve_items if c.name() == curve_data['name'])

            # Проверяем стиль линии
            line_style = curve._style_config['line_style']
            line_width = curve._style_config['width']
            qt_line_style = line_style
            excel_line_style = self.LINE_STYLE_MAP.get(qt_line_style, line_style)
            show_line = excel_line_style != 'none' and line_width > 0

            # Создаем серию данных из значений кривой
            x_data = curve.xData if hasattr(curve, 'xData') else [p.pos().x() for p in curve.scatter.points()]
            y_data = curve.yData if hasattr(curve, 'yData') else [p.pos().y() for p in curve.scatter.points()]

            # Записываем данные в лист
            start_row = self.current_row
            for i, (x, y) in enumerate(zip(x_data, y_data)):
                self.ws_data.cell(row=start_row + i, column=1, value=x)
                self.ws_data.cell(row=start_row + i, column=2, value=y)
            end_row = start_row + len(x_data) - 1

            # Создаем ссылки на диапазоны
            x_ref = Reference(self.ws_data, min_col=1, min_row=start_row, max_row=end_row)
            y_ref = Reference(self.ws_data, min_col=2, min_row=start_row, max_row=end_row)
            series = Series(y_ref, x_ref, title=curve.name())  # Основная серия с названием кривой

            # Настраиваем внешний вид точек
            if hasattr(curve, 'scatter') and curve._style_config.get('symbol') != 'none':
                # Определяем тип маркера
                if curve._style_config.get('symbol') == '*':  # Если это звезда
                    marker_symbol = 'star'
                    marker_size = 15
                else:
                    marker_symbol = curve_data['symbol']
                    marker_size = curve.point_size

                # Сначала пробуем получить цвет из символа
                symbol_brush = curve.opts.get('symbolBrush')
                if symbol_brush and hasattr(symbol_brush, 'color'):
                    marker_color = self._get_excel_color(symbol_brush.color())
                else:
                    # Если нет цвета символа, используем цвет линии
                    marker_color = self._get_excel_color(QColor(curve._style_config['color']))

                series.marker = Marker(
                    symbol=marker_symbol,
                    size=marker_size,
                    spPr=GraphicalProperties(
                        solidFill=ColorChoice(srgbClr=marker_color),
                        ln=LineProperties(solidFill=ColorChoice(srgbClr=marker_color))
                    )
                )
            else:
                # Для интерполированных кривых или кривых без символов отключаем маркеры
                series.marker = Marker(symbol='none')

            # Настраиваем линию
            if not show_line:
                series.graphicalProperties.line.noFill = True
            else:
                # Для интерполированных кривых берем цвет из pen
                line_color = self._get_excel_color(QColor(curve._style_config['color']))
                line_props = LineProperties(solidFill=ColorChoice(srgbClr=line_color))
                line_props.prstDash = excel_line_style
                line_props.w = int(line_width * 9525)
                series.graphicalProperties.line = line_props

            # Добавляем выделенные точки как отдельную серию
            if curve_data['selected_points']:
                selected_x = []
                selected_y = []

                for idx in curve_data['selected_points']:
                    selected_x.append(x_data[idx])
                    selected_y.append(y_data[idx])

                # Записываем выделенные точки
                sel_start_row = self.current_row + len(x_data) + 1
                for i, (x, y) in enumerate(zip(selected_x, selected_y)):
                    self.ws_data.cell(row=sel_start_row + i, column=1, value=x)
                    self.ws_data.cell(row=sel_start_row + i, column=2, value=y)
                sel_end_row = sel_start_row + len(selected_x) - 1

                # Создаем ссылки для выделенных точек
                sel_x_ref = Reference(self.ws_data, min_col=1, min_row=sel_start_row, max_row=sel_end_row)
                sel_y_ref = Reference(self.ws_data, min_col=2, min_row=sel_start_row, max_row=sel_end_row)
                # Изменяем название серии для выделенных точек
                selected_series = Series(sel_y_ref, sel_x_ref, title=f"Выделенные точки ({curve.name()})")

                selected_line_props = LineProperties(solidFill=ColorChoice(srgbClr="FF0000"))
                selected_line_props.w = int(9525 * 1.5)

                selected_series.marker = Marker(
                    symbol=curve_data['symbol'],
                    size=curve.point_size * (1 + curve.selected_curve_point_size),
                    spPr=GraphicalProperties(
                        solidFill=ColorChoice(srgbClr="FF0000"),
                        ln=selected_line_props
                    )
                )

                selected_series.graphicalProperties.line.noFill = True

                chart.series.append(selected_series)
                self.current_row = sel_end_row + 2
            else:
                self.current_row = end_row + 2

            chart.series.append(series)

        self.ws_plot.add_chart(chart, "B2")
        chart.height = 20
        chart.width = 30
