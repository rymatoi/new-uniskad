import ast
import json

from PySide2.QtCore import QSortFilterProxyModel, QModelIndex, QRegExp, Qt, QItemSelection
from PySide2.QtGui import QColor
from PySide2.QtWidgets import *

from app.plugins.base_state.widgets import ExtendedComboBox
from app.plugins.project import utils_ as utils
from app.plugins.work_data.models import WorkDataTreeModel
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_test import Ui_EditTestDialog
import pyqtgraph as pg
from pyqtgraph import ColorButton, PlotWidget


class FilterWidget(QWidget):
    def __init__(self, number, param_list, style=None, parent=None):
        super().__init__()
        self._style = style
        self.point_types_dict = {}
        self._parent = parent
        layout = QHBoxLayout()
        form = QFormLayout()
        self.number = number
        self.lineedit = QLineEdit()
        self.label = QLabel(f"{self.number}) Параметр Х:")
        self.Xcombobox = ExtendedComboBox()

        hlayout = QHBoxLayout()
        x_label = QLabel("X")
        self.condition_combobox = ExtendedComboBox()
        self.y_na_label = QLabel("Y на ")
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setDecimals(3)
        self.spinbox.setMinimum(0.0)
        self.spinbox.setMaximum(100)
        self.spinbox.setSuffix('%')

        hlayout.addStretch()
        hlayout.addWidget(x_label)
        hlayout.addWidget(self.condition_combobox)
        hlayout.addWidget(self.y_na_label)
        hlayout.addWidget(self.spinbox)

        y_label = QLabel('Параметр Y: ')
        self.Ycombobox = ExtendedComboBox()

        self.init_comboboxes(param_list)

        remove_button = QPushButton('Удалить фильтр')
        remove_button.clicked.connect(lambda: self.remove_filter(self.number))

        form.addRow(self.label, self.Xcombobox)
        form.addRow(y_label, self.Ycombobox)
        form.addRow(QLabel("Условие битости X: "), hlayout)

        form.addRow(remove_button)

        layout.addLayout(form)

        self.setLayout(layout)
        self.setFixedHeight(130)

        self.init_style()

    def remove_filter(self, num):
        self._parent.recount_filters(num)
        self.setParent(None)
        self.deleteLater()

    def init_comboboxes(self, param_list):
        self.Xcombobox.addItems(param_list)
        self.Ycombobox.addItems(param_list)
        self.condition_combobox.addItems(['>', '<', '='])
        self.condition_combobox.currentTextChanged.connect(lambda text: self.manage_suffix())
        # if self._parent.condition_parameter is not None:
        #     self.combobox.setCurrentText(self._parent.condition_parameter)

    def manage_suffix(self):
        if self.condition_combobox.currentText() == '=':
            self.spinbox.setSuffix('')
            self.spinbox.setMinimum(-10000)
            self.spinbox.setMaximum(10000)
            self.y_na_label.hide()
        else:
            self.spinbox.setSuffix('%')
            self.spinbox.setMinimum(0)
            self.spinbox.setMaximum(100)
            self.y_na_label.show()

    def update(self):
        self.label.setText(f"{self.number}) Параметр Х:")
        # self.combobox.setCurrentText(self._parent.condition_parameter)
        # if self.number != 1:
        #     self.combobox.setEnabled(False)
        # else:
        #     self.combobox.setEnabled(True)

    def init_style(self):
        if self._style:
            self.Xcombobox.setCurrentText(self._style['x'])
            self.Ycombobox.setCurrentText(self._style['y'])
            self.condition_combobox.setCurrentText(self._style['condition'])
            self.spinbox.setValue(self._style['condition_percent'])


class ConditionWidget(QWidget):
    def __init__(self, number, param_list, style=None, parent=None):
        super().__init__()
        self._style = style
        self.point_types_dict = {}
        self._parent = parent
        layout = QHBoxLayout()
        form = QFormLayout()
        self.number = number
        self.lineedit = QLineEdit()
        self.label = QLabel(f"Выбрать параметр для сортировки:")
        self.label_name = QLabel(f"{self.number}) Название: ")
        self.combobox = ExtendedComboBox()
        self.name_lineedit = QLineEdit(self)
        self.init_combobox(param_list)

        self.color = ColorButton()
        self.type_combobox = QComboBox()
        self.point_size = QSpinBox()
        self.type_point_combo_box()

        remove_button = QPushButton('Удалить условие')
        remove_button.clicked.connect(lambda: self.remove_condition(self.number))

        form.addRow(self.label_name, self.name_lineedit)
        form.addRow(self.label, self.combobox)
        form.addRow(QLabel("Условия отображения, если X = "), self.lineedit)
        form.addRow(QLabel("Цвет"), self.color)
        form.addRow(QLabel('Вид точки'), self.type_combobox)
        form.addRow(QLabel('Размер точки'), self.point_size)
        form.addRow(remove_button)

        layout.addLayout(form)

        self.setLayout(layout)
        self.setFixedHeight(210)

        self.init_style()

    def init_style(self):
        if self._style:
            self.name_lineedit.setText(self._style.get('name',
                                                       self._parent.item.curve_name if self._parent.item.curve_name else self._parent.item.name))
            self.color.setColor(QColor(self._style['color']))
            self.combobox.setCurrentText(self._style['x'])
            self.lineedit.setText(self._style['val'])
            self.type_combobox.setCurrentText(self.point_types_dict[self._style['type']])
            self.point_size.setValue(self._style['point_size'])
        else:
            self.name_lineedit.setText(
                self._parent.item.curve_name if self._parent.item.curve_name else self._parent.item.name)

    def init_combobox(self, param_list):
        self.combobox.addItems(param_list)
        self.combobox.currentTextChanged.connect(lambda text: self._parent.update_comboboxes(text))
        if self._parent.condition_parameter is not None:
            self.combobox.setCurrentText(self._parent.condition_parameter)

    def remove_condition(self, num):
        self._parent.recount_conditions(num)
        self.setParent(None)
        self.deleteLater()

    def update(self):
        self.label.setText(f"{self.number})   Выбрать параметр для сортировки:")
        self.combobox.setCurrentText(self._parent.condition_parameter)
        if self.number != 1:
            self.combobox.setEnabled(False)
        else:
            self.combobox.setEnabled(True)

    def type_point_combo_box(self):
        """Функция заполнения списка типов точки."""
        # Указываются наименования стандартных типов точек в порядке,
        # соответствующем зарезервированным символьным константам (POINT_TYPES)
        self.point_types_dict = {
            k: v for k, v in utils.SYMBOLS
        }
        self.type_combobox.addItems(list(self.point_types_dict.values()))


class EditProjectItemDialog(BaseDialog):
    CONDITIONS_CLIPBOARD_KEY = "__uniskad_test_conditions__"
    FILTERS_CLIPBOARD_KEY = "__uniskad_test_filters__"

    LINE_STYLES = [
        (Qt.NoPen, 'Прозрачная'),
        (Qt.SolidLine, 'Линия'),
        (Qt.DashLine, 'Пунктирная линия'),
        (Qt.DotLine, 'Линия из точек'),
        (Qt.DashDotLine, 'Линия точка-тире'),
        (Qt.DashDotDotLine, 'Линия точка-точка-тире'),
    ]

    # Символьные константы, которые определяют тип отображения точки на графике
    # POINT_SYMBOLS = [
    #     ('o', 'Круг'),
    #     ('s', 'Квадрат'),
    #     ('t', 'Треугольник'),
    #     ('d', 'Ромб'),
    #     ('+', 'Плюс'),
    # ]

    def __init__(self, item, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.item = item
        self.ui = Ui_EditTestDialog()
        self.ui.setupUi(self)

        self.curves = None
        self.condition_parameter = None
        self.filter_parameter = None
        self.init_param_list()

        self.example_plot = pg.PlotDataItem([0, 1], [0, 1])

        self.setFocus(Qt.OtherFocusReason)
        self.type_line_combo_box()  # вызов функций с инициаизаций полей выбора параметров линии
        self.type_point_combo_box()

        self.init_conditions()
        self.init_filters()

        self.init_values(self.item)  # задание отображаемого графика-примера

        # Задание внешнего вида у графической области в диалоге настройки линии
        self.ui.plotView.plotItem.getAxis('bottom').setStyle(showValues=False)
        self.ui.plotView.plotItem.getAxis('left').setStyle(showValues=False)
        self.ui.plotView.plotItem.setRange(xRange=[0, 1], yRange=[0, 1], padding=0.05)
        self.ui.plotView.plotItem.showGrid(True, True, 0.7)
        self.ui.plotView.plotItem.vb.setMouseEnabled(x=False, y=False)
        self.ui.plotView.plotItem.addItem(self.example_plot)  # Добавляем кривую-образец
        self.refresh()
        self.ui.groupBox.setMinimumHeight(380)

        if self.item.internal_type() != 'test':
            self.ui.groupBox_3.setEnabled(False)

        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept_)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.close)
        self.ui.colorButton.sigColorChanged.connect(self.refresh)
        self.ui.lineType.currentIndexChanged.connect(self.refresh)
        self.ui.thickness.valueChanged.connect(self.refresh)
        self.ui.pointType.currentIndexChanged.connect(self.refresh)
        self.ui.pointSizeSpinBox.valueChanged.connect(self.refresh)
        self.ui.addConditionButton.clicked.connect(self.add_condition)
        self.ui.addConditionButton_2.clicked.connect(self.add_filter)
        self.ui.copyButton.clicked.connect(self.copy_conditions_to_clipboard)
        self.ui.pasteButton.clicked.connect(self.paste_conditions_from_clipboard)
        self.ui.copyButton_2.clicked.connect(self.copy_filters_to_clipboard)
        self.ui.pasteButton_2.clicked.connect(self.paste_filters_from_clipboard)

    def set_condition_param(self, param):
        self.condition_parameter = param

    def update_comboboxes(self, text):
        if text in self.curves:
            self.condition_parameter = text
            for i in range(self.condition_count()):
                widget = self.container_lay.itemAt(i)
                condition_widget = widget.widget()
                condition_widget.combobox.setCurrentText(text)

    def init_conditions(self, ):
        self.container = QWidget(self)
        self.container_lay = QVBoxLayout(self.container)
        self.ui.scrollArea.setWidget(self.container)
        self.container_lay.addStretch()

        if self.item.conditions:
            conditions = ast.literal_eval(self.item.conditions)
            for condition in conditions:
                self.add_condition(condition)

    def init_filters(self, ):
        self.f_container = QWidget(self)
        self.f_container_lay = QVBoxLayout(self.f_container)
        self.ui.scrollArea_2.setWidget(self.f_container)
        self.f_container_lay.addStretch()

        if self.item.filters:
            filters = ast.literal_eval(self.item.filters)
            for filter in filters:
                self.add_filter(filter)

    def init_param_list(self):
        project_item = self.item.parent().parent()
        self.curves = utils.get_project_param_names(project_item._data.id)

    def add_condition(self, style=None):
        normalized_style = self._normalize_condition_payload(style, strict=False) if style else None
        condition_widget = ConditionWidget(
            self.container_lay.count(),
            self.curves,
            parent=self,
            style=normalized_style
        )
        self.container_lay.insertWidget(condition_widget.number - 1, condition_widget)
        if condition_widget.number != 1:
            condition_widget.combobox.setEnabled(False)
        return condition_widget

    def add_filter(self, style=None):
        normalized_style = self._normalize_filter_payload(style, strict=False) if style else None
        filter_widget = FilterWidget(
            self.f_container_lay.count(),
            self.curves,
            parent=self,
            style=normalized_style
        )
        self.f_container_lay.insertWidget(filter_widget.number - 1, filter_widget)
        # if filter_widget.number != 1:
        #     filter_widget.combobox.setEnabled(False)
        return filter_widget

    def condition_count(self):
        return self.container_lay.count() - 1

    def filter_count(self):
        return self.f_container_lay.count() - 1

    def recount_conditions(self, num):
        count = self.condition_count()
        if count == 1:
            self.condition_parameter = None
        for i in range(count):
            widget = self.container_lay.itemAt(i)
            condition_widget = widget.widget()
            if condition_widget.number > num:
                condition_widget.number -= 1
                condition_widget.update()

    def recount_filters(self, num):
        count = self.filter_count()
        if count == 1:
            self.filter_parameter = None
        for i in range(count):
            widget = self.f_container_lay.itemAt(i)
            filter_widget = widget.widget()
            if filter_widget.number > num:
                filter_widget.number -= 1
                filter_widget.update()

    def init_values(self, curve):

        if self.item.curve_color is None:
            curve.curve_line_style = 1
            curve.curve_point_symbol = 'o'
            curve.curve_color = 'black'
            curve.curve_symbol_color = 'black'
            curve.curve_symbol_fill_color = 'black'
            curve.curve_point_size = 3
            curve.curve_width = 1

        # TODO может быть сделать выгрузку значений по умолчанию здесь?
        self.ui.curveNameLineEdit.setText(self.item.curve_name if self.item.curve_name is not None else '')
        line_type_index = next(i for i, (k, v) in enumerate(utils.LINE_STYLES) if k == int(curve.curve_line_style))
        point_type_index = next(i for i, (k, v) in enumerate(utils.SYMBOLS) if k == curve.curve_point_symbol)
        self.ui.colorButton.setColor(QColor(curve.curve_color))  # Задаем цвет кривой
        self.ui.colorButton_3.setColor(QColor(curve.curve_symbol_color))  # Задаем цвет кривой
        self.ui.colorButton_2.setColor(QColor(curve.curve_symbol_fill_color))  # Задаем цвет кривой
        self.ui.lineType.setCurrentIndex(line_type_index)  # Задаем цвет кривой
        self.ui.thickness.setValue(int(curve.curve_width))  # устанавливае толщину линии
        self.ui.pointType.setCurrentIndex(point_type_index)  # устанавливае толщину линии
        self.ui.pointSizeSpinBox.setValue(int(curve.curve_point_size))  # устанавливае толщину линии
        if isinstance(self.item.display_as_curve, str):
            self.item.display_as_curve = True if self.item.display_as_curve == 'True' else False
        self.ui.displayCheckBox.setChecked(self.item.display_as_curve)
        if isinstance(self.item.use_conditions, str):
            self.item.use_conditions = True if self.item.use_conditions == 'True' else False

        if isinstance(self.item.use_filters, str):
            self.item.use_filters = True if self.item.use_filters == 'True' else False

        self.ui.applyCheckBox.setChecked(self.item.use_conditions)
        self.ui.applyCheckBox_2.setChecked(self.item.use_filters)

    def refresh(self):
        """Обновление выбранных данных на интерфейсе"""
        color = self.ui.colorButton.color()
        s_color = self.ui.colorButton_3.color()
        sf_color = self.ui.colorButton_2.color()
        width = self.ui.thickness.value()
        line_style = self.LINE_STYLES[self.ui.lineType.currentIndex()][0]
        symbol = utils.SYMBOLS[self.ui.pointType.currentIndex()][0]
        point_size = self.ui.pointSizeSpinBox.value()

        self.example_plot.setSymbol(symbol)
        self.example_plot.setSymbolPen(s_color)
        self.example_plot.setSymbolBrush(sf_color)
        self.example_plot.setSymbolSize(point_size)
        self.example_plot.setPen(color=color, width=width, style=line_style)

    def type_line_combo_box(self):
        """Функция заполнения списка типов линии"""
        # Указываются стандартные типы линий в порядке зарезервированных за ними констант
        line_styles = [name for _, name in self.LINE_STYLES]
        self.ui.lineType.addItems(line_styles)

    def type_point_combo_box(self):
        """Функция заполнения списка типов точки."""
        # Указываются наименования стандартных типов точек в порядке,
        # соответствующем зарезервированным символьным константам (POINT_TYPES)
        point_symbols = [name for _, name in utils.SYMBOLS]
        self.ui.pointType.addItems(point_symbols)

    def accept_(self) -> None:
        curve = self.item
        curve.curve_name = self.ui.curveNameLineEdit.text()
        curve.curve_color = self.ui.colorButton.color().name()
        curve.curve_symbol_color = self.ui.colorButton_3.color().name()
        curve.curve_symbol_fill_color = self.ui.colorButton_2.color().name()
        curve.curve_width = self.ui.thickness.value()
        curve.curve_line_style = self.LINE_STYLES[self.ui.lineType.currentIndex()][0]
        curve.curve_point_symbol = utils.SYMBOLS[self.ui.pointType.currentIndex()][0]
        curve.curve_point_size = self.ui.pointSizeSpinBox.value()
        curve.display_as_curve = self.ui.displayCheckBox.isChecked()

        conditions = self._collect_conditions()
        filters = self._collect_filters()

        styles = (
            ('curve_width', f'{curve.curve_width}'),
            ('curve_color', curve.curve_color),
            ('curve_symbol_color', curve.curve_symbol_color),
            ('curve_symbol_fill_color', curve.curve_symbol_fill_color),
            ('curve_line_style', int(curve.curve_line_style)),
            ('curve_point_symbol', curve.curve_point_symbol),
            ('curve_point_size', curve.curve_point_size),
            ('curve_name', curve.curve_name),
            ('display_as_curve', curve.display_as_curve),
            ('conditions', str(conditions)),
            ('filters', str(filters)),
            ('use_conditions', self.ui.applyCheckBox.isChecked()),
            ('use_filters', self.ui.applyCheckBox_2.isChecked()),
        )

        props = []
        for prop_name, prop_value in styles:
            props.append((
                None,
                curve._data.id,
                curve._data.id_up,
                7,
                prop_name,
                str(prop_value),
                None,
                None,
                None,
                0,
                None
            ))

        props = sp.new_update_project_from_record_array(props)
        self.item.update_class_props(props)
        super().accept()

    def _collect_conditions(self):
        conditions = []
        for i in range(self.condition_count()):
            item = self.container_lay.itemAt(i)
            condition_widget = item.widget()
            if condition_widget is None:
                continue

            x = condition_widget.combobox.currentText()
            if x in self.curves:
                conditions.append({
                    'name': condition_widget.name_lineedit.text(),
                    'x': x,
                    'val': condition_widget.lineedit.text(),
                    'color': condition_widget.color.color().name(),
                    'point_size': condition_widget.point_size.value(),
                    'type': utils.SYMBOLS[condition_widget.type_combobox.currentIndex()][0]
                })
        return conditions

    def _collect_filters(self):
        filters = []
        for i in range(self.filter_count()):
            item = self.f_container_lay.itemAt(i)
            filter_widget = item.widget()
            if filter_widget is None:
                continue

            x = filter_widget.Xcombobox.currentText()
            y = filter_widget.Ycombobox.currentText()
            _condition = filter_widget.condition_combobox.currentText()
            percents = filter_widget.spinbox.value()
            if x in self.curves and y in self.curves:
                filters.append({
                    'x': x,
                    'y': y,
                    'condition': _condition,
                    'condition_percent': percents
                })
        return filters

    def copy_conditions_to_clipboard(self):
        payload = {
            'type': self.CONDITIONS_CLIPBOARD_KEY,
            'conditions': self._collect_conditions(),
            'use_conditions': self.ui.applyCheckBox.isChecked()
        }
        self._set_clipboard_payload(payload)

    def paste_conditions_from_clipboard(self):
        payload = self._read_clipboard_payload(self.CONDITIONS_CLIPBOARD_KEY)
        if payload is None:
            self._show_clipboard_warning('Буфер обмена не содержит сохраненных условий.')
            return

        conditions = payload.get('conditions')
        if not isinstance(conditions, list):
            self._show_clipboard_warning('Некорректный формат данных условий в буфере обмена.')
            return

        self._set_conditions_from_data(conditions)
        if 'use_conditions' in payload:
            self.ui.applyCheckBox.setChecked(bool(payload['use_conditions']))

    def copy_filters_to_clipboard(self):
        payload = {
            'type': self.FILTERS_CLIPBOARD_KEY,
            'filters': self._collect_filters(),
            'use_filters': self.ui.applyCheckBox_2.isChecked()
        }
        self._set_clipboard_payload(payload)

    def paste_filters_from_clipboard(self):
        payload = self._read_clipboard_payload(self.FILTERS_CLIPBOARD_KEY)
        if payload is None:
            self._show_clipboard_warning('Буфер обмена не содержит сохраненных фильтров.')
            return

        filters = payload.get('filters')
        if not isinstance(filters, list):
            self._show_clipboard_warning('Некорректный формат данных фильтров в буфере обмена.')
            return

        self._set_filters_from_data(filters)
        if 'use_filters' in payload:
            self.ui.applyCheckBox_2.setChecked(bool(payload['use_filters']))

    def _set_conditions_from_data(self, conditions):
        self._clear_conditions()
        sanitized = [self._normalize_condition_payload(cond, strict=True) for cond in conditions]
        sanitized = [cond for cond in sanitized if cond is not None]

        for condition in sanitized:
            self.add_condition(condition)

    def _set_filters_from_data(self, filters):
        self._clear_filters()
        sanitized = [self._normalize_filter_payload(flt, strict=True) for flt in filters]
        sanitized = [flt for flt in sanitized if flt is not None]

        for filter_style in sanitized:
            self.add_filter(filter_style)

    def _clear_conditions(self):
        for i in reversed(range(self.condition_count())):
            item = self.container_lay.itemAt(i)
            widget = item.widget()
            if widget is None:
                continue
            self.container_lay.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.condition_parameter = None

    def _clear_filters(self):
        for i in reversed(range(self.filter_count())):
            item = self.f_container_lay.itemAt(i)
            widget = item.widget()
            if widget is None:
                continue
            self.f_container_lay.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

    def _normalize_condition_payload(self, data, strict=True):
        if not isinstance(data, dict):
            return None

        x = data.get('x')
        if not x:
            return None
        if strict and x not in self.curves:
            return None

        name = data.get('name')
        try:
            name = '' if name is None else str(name)
        except Exception:
            name = ''

        val = data.get('val', '')
        try:
            val = str(val)
        except Exception:
            val = ''

        color = data.get('color') or '#000000'
        if not QColor(color).isValid():
            color = '#000000'

        valid_symbols = {symbol for symbol, _ in utils.SYMBOLS}
        default_symbol = utils.SYMBOLS[0][0] if utils.SYMBOLS else 'o'
        symbol = data.get('type') or default_symbol
        if symbol not in valid_symbols:
            symbol = default_symbol

        try:
            point_size = int(data.get('point_size', 3))
        except (TypeError, ValueError):
            point_size = 3

        return {
            'name': name,
            'x': x,
            'val': val,
            'color': color,
            'point_size': point_size,
            'type': symbol
        }

    def _normalize_filter_payload(self, data, strict=True):
        if not isinstance(data, dict):
            return None

        x = data.get('x')
        y = data.get('y')
        if not x or not y:
            return None
        if strict and (x not in self.curves or y not in self.curves):
            return None

        condition = data.get('condition', '>')
        if condition not in ('>', '<', '='):
            condition = '>'

        percent = data.get('condition_percent', 0)
        try:
            percent = float(percent)
        except (TypeError, ValueError):
            percent = 0.0

        return {
            'x': x,
            'y': y,
            'condition': condition,
            'condition_percent': percent
        }

    def _set_clipboard_payload(self, payload):
        QApplication.clipboard().setText(json.dumps(payload, ensure_ascii=False))

    def _read_clipboard_payload(self, expected_type):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return None
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict) or payload.get('type') != expected_type:
            return None
        return payload

    def _show_clipboard_warning(self, message):
        QMessageBox.warning(self, 'Буфер обмена', message)

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
