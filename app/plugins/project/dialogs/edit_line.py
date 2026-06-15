import json

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from app.plugins.project import utils
from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.widgets.colors import safe_color
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_line import Ui_EditLineDialog
import pyqtgraph as pg


class EditLineDialog(BaseDialog):
    LINE_STYLES = [
        (Qt.NoPen, 'Прозрачная'),
        (Qt.SolidLine, 'Линия'),
        (Qt.DashLine, 'Пунктирная линия'),
        (Qt.DotLine, 'Линия из точек'),
        (Qt.DashDotLine, 'Линия точка-тире'),
        (Qt.DashDotDotLine, 'Линия точка-точка-тире'),
    ]

    def __init__(self, item, parent=None, flags=None):
        super().__init__(parent, flags)
        self.item = item
        self.result_style = None
        self.ui = Ui_EditLineDialog()
        self.ui.setupUi(self)

        self.example_plot = pg.PlotDataItem([0, 1], [0, 1])

        self.setFocus(Qt.OtherFocusReason)
        self.type_line_combo_box()  # вызов функций с инициаизаций полей выбора параметров линии
        self.type_point_combo_box()
        self.init_values(self.item)  # задание отображаемого графика-примера

        # Задание внешнего вида у графической области в диалоге настройки линии
        self.ui.plotView.plotItem.getAxis('bottom').setStyle(showValues=False)
        self.ui.plotView.plotItem.getAxis('left').setStyle(showValues=False)
        self.ui.plotView.plotItem.setRange(xRange=[0, 1], yRange=[0, 1], padding=0.05)
        self.ui.plotView.plotItem.showGrid(True, True, 0.7)
        self.ui.plotView.plotItem.vb.setMouseEnabled(x=False, y=False)
        self.ui.plotView.plotItem.addItem(self.example_plot)  # Добавляем кривую-образец
        self.refresh()
        self.create_connections()  # создаем привязки

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept_)
        self.ui.colorButton.sigColorChanged.connect(self.refresh)
        self.ui.lineType.currentIndexChanged.connect(self.refresh)
        self.ui.thickness.valueChanged.connect(self.refresh)
        self.ui.pointType.currentIndexChanged.connect(self.refresh)
        self.ui.pointSizeSpinBox.valueChanged.connect(self.refresh)

    def init_values(self, curve):
        if hasattr(self.item, 'style_config'):
            values = visual_style_to_dialog_style(
                getattr(self.item, 'style_config', {}) or {},
                self.item.name() if callable(getattr(self.item, 'name', None)) else ''
            )
            curve_line_style = values['curve_line_style']
            curve_point_symbol = values['curve_point_symbol']
            curve_color = values['curve_color']
            curve_symbol_color = values['curve_symbol_color']
            curve_symbol_fill_color = values['curve_symbol_fill_color']
            curve_point_size = values['curve_point_size']
            curve_width = values['curve_width']
            curve_name = values['curve_name']
        elif hasattr(self.item, 'internal_type'):
            if self.item.curve_color is not None:
                curve_line_style = curve.curve_line_style
                curve_point_symbol = curve.curve_point_symbol
                curve_color = curve.curve_color
                curve_symbol_color = curve.curve_symbol_color
                curve_symbol_fill_color = curve.curve_symbol_fill_color
                curve_point_size = curve.curve_point_size
                curve_width = curve.curve_width
                curve_name = self.item.curve_name if self.item.curve_name is not None else ''
            else:
                curve_line_style = 1
                curve_point_symbol = 'o'
                curve_color = 'black'
                curve_symbol_color = 'black'
                curve_symbol_fill_color = 'black'
                curve_point_size = 3
                curve_width = 1
                curve_name = ''
        else:
            if isinstance(self.item.values, str):
                self.item.values = json.loads(self.item.values)
            curve_line_style = self.item.values.get('curve_line_style', 1)
            curve_point_symbol = self.item.values.get('curve_point_symbol', 'o')
            curve_color = self.item.values.get('curve_color', 'blue')
            curve_symbol_color = self.item.values.get('curve_symbol_color', 'black')
            curve_symbol_fill_color = self.item.values.get('curve_symbol_fill_color', 'blue')
            curve_point_size = self.item.values.get('curve_point_size', 10)
            curve_width = self.item.values.get('curve_width', 1)
            curve_name = self.item.values.get('name', '')

        # TODO может быть сделать выгрузку значений по умолчанию здесь?
        self.ui.curveNameLineEdit.setText(curve_name)
        line_type_index = next((i for i, (k, _) in enumerate(utils.LINE_STYLES)
                                if int(k) == _safe_int(curve_line_style, int(Qt.SolidLine))), 1)
        point_type_index = next((i for i, (k, _) in enumerate(utils.SYMBOLS)
                                 if k == curve_point_symbol), 0)
        self.ui.colorButton.setColor(safe_color(curve_color, '#000000'))
        self.ui.colorButton_3.setColor(safe_color(curve_symbol_color, '#000000'))
        self.ui.colorButton_2.setColor(safe_color(curve_symbol_fill_color, '#000000'))
        self.ui.lineType.setCurrentIndex(line_type_index)  # Задаем цвет кривой
        self.ui.thickness.setValue(int(curve_width))  # устанавливае толщину линии
        self.ui.pointType.setCurrentIndex(point_type_index)  # устанавливае толщину линии
        self.ui.pointSizeSpinBox.setValue(int(curve_point_size))  # устанавливае толщину линии

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
        curve_name = self.ui.curveNameLineEdit.text()
        curve_color = self.ui.colorButton.color().name()
        curve_symbol_color = self.ui.colorButton_3.color().name()
        curve_symbol_fill_color = self.ui.colorButton_2.color().name()
        curve_width = self.ui.thickness.value()
        curve_line_style = self.LINE_STYLES[self.ui.lineType.currentIndex()][0]
        curve_point_symbol = utils.SYMBOLS[self.ui.pointType.currentIndex()][0]
        curve_point_size = self.ui.pointSizeSpinBox.value()
        styles = (
            ('curve_width', f'{curve_width}'),
            ('curve_color', curve_color),
            ('curve_symbol_color', curve_symbol_color),
            ('curve_symbol_fill_color', curve_symbol_fill_color),
            ('curve_line_style', int(curve_line_style)),
            ('curve_point_symbol', curve_point_symbol),
            ('curve_point_size', curve_point_size),
            ('curve_name', curve_name),
        )

        if hasattr(self.item, 'style_config'):
            self.result_style = dialog_style_to_visual_style(dict(styles))
        elif hasattr(self.item, 'internal_type'):
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
        else:
            for prop_name, prop_value in styles:
                if prop_name == 'curve_name':
                    self.item.values['name'] = prop_value
                else:
                    self.item.values[prop_name] = prop_value
            self.res = sp.new_upd_custom_curve((self.item.id, self.item.graph_project_id, json.dumps(self.item.values)))
        super().accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _color_name(value, default):
    return safe_color(value, default).name()


def visual_style_to_dialog_style(style, name=''):
    """Convert a CurveItem style to the legacy EditLineDialog representation."""
    style = style if isinstance(style, dict) else {}
    return {
        'curve_color': _color_name(style.get('color'), '#000000'),
        'curve_width': _safe_int(style.get('width'), 1),
        'curve_line_style': int(GraphConstants.resolve_pen_style(style.get('line_style'))),
        'curve_point_symbol': style.get('symbol') or 'o',
        'curve_point_size': _safe_int(style.get('symbol_size'), 10),
        'curve_symbol_color': _color_name(style.get('symbol_color'), '#000000'),
        'curve_symbol_fill_color': _color_name(style.get('fill_color'), '#000000'),
        'curve_name': style.get('name', name) or name,
    }


def dialog_style_to_visual_style(style):
    """Convert legacy ProjectData style keys to CurveItem style keys."""
    style = style if isinstance(style, dict) else {}
    return {
        'color': _color_name(style.get('curve_color'), '#000000'),
        'width': _safe_int(style.get('curve_width'), 1),
        'line_style': _safe_int(style.get('curve_line_style'), int(Qt.SolidLine)),
        'symbol': style.get('curve_point_symbol') or 'o',
        'symbol_size': _safe_int(style.get('curve_point_size'), 10),
        'symbol_color': _color_name(style.get('curve_symbol_color'), '#000000'),
        'fill_color': _color_name(style.get('curve_symbol_fill_color'), '#000000'),
        'name': style.get('curve_name', style.get('name', '')),
    }
