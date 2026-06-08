from PySide6.QtWidgets import *

from app.basic_funcs import to_float
from app.plugins.base_state.widgets import ExtendedComboBox
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_conditions_dialog import Ui_AddConditionsDialog

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QRegularExpression, Qt, QItemSelection
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialogButtonBox

from app.plugins.work_data.models import WorkDataTreeModel
from db import sp
from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_edit_test import Ui_EditTestDialog
import pyqtgraph as pg
from resources.ui.ui_py.ui_select_test_dialog import Ui_SelectTestDialog


class EditProjectItemDialog(BaseDialog):
    LINE_STYLES = [
        (Qt.PenStyle.NoPen, 'Прозрачная'),
        (Qt.PenStyle.SolidLine, 'Линия'),
        (Qt.PenStyle.DashLine, 'Пунктирная линия'),
        (Qt.PenStyle.DotLine, 'Линия из точек'),
        (Qt.PenStyle.DashDotLine, 'Линия точка-тире'),
        (Qt.PenStyle.DashDotDotLine, 'Линия точка-точка-тире'),
    ]

    # Символьные константы, которые определяют тип отображения точки на графике
    POINT_SYMBOLS = [
        ('o', 'Круг'),
        ('s', 'Квадрат'),
        ('t', 'Треугольник'),
        ('d', 'Ромб'),
        ('+', 'Плюс'),
    ]

    def __init__(self, styles, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.styles = styles
        self.ui = Ui_EditTestDialog()
        self.ui.setupUi(self)

        self.example_plot = pg.PlotDataItem([0, 1], [0, 1])

        self.setFocus(Qt.FocusReason.OtherFocusReason)
        self.type_line_combo_box()  # вызов функций с инициаизаций полей выбора параметров линии
        self.type_point_combo_box()
        self.init_values(self.styles)  # задание отображаемого графика-примера

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
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.close)
        self.ui.colorButton.sigColorChanged.connect(self.refresh)
        self.ui.lineType.currentIndexChanged.connect(self.refresh)
        self.ui.thickness.valueChanged.connect(self.refresh)
        self.ui.pointType.currentIndexChanged.connect(self.refresh)
        self.ui.pointSizeSpinBox.valueChanged.connect(self.refresh)

    def init_values(self, curve):
        # TODO может быть сделать выгрузку значений по умолчанию здесь?
        self.ui.curveNameLineEdit.setText(self.styles.get('curve_name', ''))
        line_type_index = next(
            i for i, (k, v) in enumerate(self.LINE_STYLES) if k == int(self.styles.get('curve_line_style', 1)))
        point_type_index = next(
            i for i, (k, v) in enumerate(self.POINT_SYMBOLS) if k == self.styles.get('curve_point_symbol', 'o'))
        self.ui.colorButton.setColor(QColor(self.styles.get('curve_color', 'black')))  # Задаем цвет кривой
        self.ui.lineType.setCurrentIndex(line_type_index)  # Задаем цвет кривой
        self.ui.thickness.setValue(int(self.styles.get('curve_width', 1)))  # устанавливае толщину линии
        self.ui.pointType.setCurrentIndex(point_type_index)  # устанавливае толщину линии
        self.ui.pointSizeSpinBox.setValue(int(self.styles.get('curve_point_size', 3)))  # устанавливае толщину линии
        self.ui.displayCheckBox.setHidden(True)
        self.ui.label_2.setHidden(True)

    def refresh(self):
        """Обновление выбранных данных на интерфейсе"""
        color = self.ui.colorButton.color()
        width = self.ui.thickness.value()
        line_style = self.LINE_STYLES[self.ui.lineType.currentIndex()][0]
        symbol = self.POINT_SYMBOLS[self.ui.pointType.currentIndex()][0]
        point_size = self.ui.pointSizeSpinBox.value()

        self.example_plot.setSymbol(symbol)
        self.example_plot.setSymbolPen(color)
        self.example_plot.setSymbolBrush(None)
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
        point_symbols = [name for _, name in self.POINT_SYMBOLS]
        self.ui.pointType.addItems(point_symbols)

    def accept(self) -> None:
        styles = {'curve_width': f'{self.ui.thickness.value()}',
                  'curve_color': self.ui.colorButton.color().name(),
                  'curve_line_style': self.LINE_STYLES[self.ui.lineType.currentIndex()][0],
                  'curve_point_symbol': self.POINT_SYMBOLS[self.ui.pointType.currentIndex()][0],
                  'curve_point_size': self.ui.pointSizeSpinBox.value(),
                  'curve_name': self.ui.curveNameLineEdit.text()
                  }

        self.res = styles

        super().accept()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()


class ConditionWidget(QWidget):
    def __init__(self, number, param_list, parent=None):
        super().__init__()
        self._parent = parent
        layout = QFormLayout()
        self.number = number
        self.lineedit = QLineEdit()
        self.label = QLabel(f"{self.number})   Выбрать параметр для сортировки:")
        self.combobox = ExtendedComboBox()
        self.init_combobox(param_list)

        remove_button = QPushButton('Удалить условие')
        remove_button.clicked.connect(lambda: self.remove_condition(self.number))

        settings_button = QPushButton('Настройка элемента')
        settings_button.clicked.connect(lambda: self.edit_condition(self.number))

        layout.addRow(self.label, self.combobox)
        layout.addRow(QLabel("Условия отображения, если X = "), self.lineedit)
        layout.addRow(settings_button, remove_button)

        self.setLayout(layout)

    def init_combobox(self, param_list):
        self.combobox.addItems(param_list)

    def remove_condition(self, num):
        self._parent.recount_conditions(num)
        self.setParent(None)
        self.deleteLater()

    def edit_condition(self, num):
        dialog = EditProjectItemDialog(self)
        if dialog.exec():
            pass

    def update(self):
        self.label.setText(f"{self.number})   Выбрать параметр для сортировки:")


class ConditionsDialog(BaseDialog):

    def __init__(self, item, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.item = item
        self.ui = Ui_AddConditionsDialog()
        self.ui.setupUi(self)
        self.container = QWidget(self)
        self.container_lay = QVBoxLayout(self.container)
        self.ui.scrollArea.setWidget(self.container)
        self.container_lay.addStretch()

        self.init_param_list()
        self.create_connections()

    def init_param_list(self):
        project_item = self.item.parent().parent()
        self.curves = sp.get_project_test_params(project_item._data.id)

    def condition_count(self):
        return self.container_lay.count() - 1

    def recount_conditions(self, num):
        for i in range(self.condition_count()):
            widget = self.container_lay.itemAt(i)
            condition_widget = widget.widget()
            if condition_widget.number > num:
                condition_widget.number -= 1
                condition_widget.update()

    def add_condition(self):
        condition_widget = ConditionWidget(self.container_lay.count(), self.curves, self)
        self.container_lay.insertWidget(condition_widget.number - 1, condition_widget)

    def create_connections(self):
        """Создание привязок для обработки кнопок"""
        self.ui.cancelButton.clicked.connect(self.cancel)
        self.ui.addConditionButton.clicked.connect(self.add_condition)
        self.ui.acceptButton.clicked.connect(self.accept)

    def accept(self) -> None:
        result_json = {}
        conditions = []
        for i in range(self.condition_count()):
            widget = self.container_lay.itemAt(i)
            condition_widget = widget.widget()
            conditions.append({
                'x': condition_widget.combobox.currentText(),
                'val': condition_widget.lineedit.text(),
            })

        super().accept()

    def cancel(self):
        """Обработка кнопки отмены """
        self.close()

    @classmethod
    def modal(cls, parent=None):
        """Запуск модального окна"""
        wnd = cls(parent)
        return wnd.exec()
