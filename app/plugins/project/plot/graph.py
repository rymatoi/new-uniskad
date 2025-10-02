import json
from collections import defaultdict
from copy import copy, deepcopy
import ast
import PySide2
import numpy as np
from itertools import chain

from PySide2 import QtCore
from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QColor, QCursor
from PySide2.QtWidgets import QMenu, QApplication, QInputDialog
from pyqtgraph import Point, ItemSample
from scipy.interpolate import interp1d

from app import _menu, app_logger, basic_funcs
from app.basic_funcs import to_float, to_bool, float_to_excel, excel_to_float, timing_decorator
from app.history_manager.events import LegendPositionChangeEvent
from app.plugins.project import utils, utils_
from app.plugins.project.dialogs.create_approx import ApproxDialog
from app.plugins.project.dialogs.create_interpolation import InterpDialog
from app.plugins.project.dialogs.edit_line import EditLineDialog
from app.plugins.project.dialogs.extrapolation_dialog import ExtrapolationDialog
from app.plugins.project.dialogs.legend_settings_dialog import LegendSettingsDialog
from app.plugins.project.plot.ruler import Ruler
from app.plugins.project.utils_ import compare_floats
from db import sp
from db.tables import PROJECT_TABLE
import pyqtgraph as pg

logger = app_logger.get_logger(__name__)


class EpureCustomSample(ItemSample):

    def mouseClickEvent(self, event):
        """Use the mouseClick event to toggle the visibility of the plotItem
        """
        if event.button() == Qt.MouseButton.LeftButton:
            plot_view = self.parentItem()._parent
            visible = self.item.isVisible()
            # self.item.setVisible(not visible)

            for item in plot_view.plotItem.items:
                if item.test_node._data.project_id == self.item.test_node._data.project_id:
                    item.setVisible(not visible)

        event.accept()
        self.update()


class GraphCustomSample(ItemSample):
    def mouseClickEvent(self, event):
        """Use the mouseClick event to toggle the visibility of the plotItem
        """
        if event.button() == Qt.MouseButton.LeftButton:
            plot_view = self.parentItem()._parent
            visible = self.item.isVisible()
            # self.item.setVisible(not visible)

            if self.item.group_by_item:
                for item in plot_view.plotItem.items:
                    if item.group_by_item is not None:
                        if item.group_by_item._data.project_id == self.item.group_by_item._data.project_id:
                            item.setVisible(not visible)
            else:
                self.item.setVisible(not visible)

        event.accept()
        self.update()


class CustomLegend(pg.LegendItem):
    """
    Класс легенды

    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent
        self.old_pos = None
        self.last_pos_offset = None  # смещение от начальной точки
        self.current_pos = None  # текущее положение легенды

        self.available_actions = []
        self.legend_menu = self._load_menu('any', 'legend')
        self._legend_settings = self._collect_settings()
        self._apply_settings()

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def setOffset(self, offset):
        super().setOffset(offset)
        self.last_pos_offset = Point(offset)
        self.calculate_pos()

    def event(self, event: PySide2.QtCore.QEvent) -> bool:
        if event.type() == QEvent.UngrabMouse:
            self._parent.main_window.event_stack.add_event(
                LegendPositionChangeEvent(self, self.old_pos, self.current_pos))
        return super().event(event)

    def mouseDragEvent(self, ev):
        """
        Перемещение легенды, просчитывает новое положение
        """
        super().mouseDragEvent(ev)

        self.calculate_pos()
        self.last_pos_offset += ev.pos() - ev.lastPos()

    def calculate_pos(self):
        anchorx = 1 if self.last_pos_offset.x() <= 0 else 0
        anchory = 1 if self.last_pos_offset.y() <= 0 else 0
        anchor = (anchorx, anchory)

        o = self.mapToParent(Point(0, 0))
        a = self.boundingRect().bottomRight() * Point(anchor)
        a = self.mapToParent(a)
        p = self.parentItem().boundingRect().bottomRight() * Point(anchor)
        off = Point(self.last_pos_offset)

        self.old_pos = self.current_pos
        self.current_pos = p + (o - a) + off

    def update_pos(self, pos):
        if pos is not None:
            self.setOffset(pos)

    def on_context_menu(self, pos):
        pass
        # menu = self.menu(pos)
        # menu.exec_(QCursor.pos())

    def menu(self, pos):
        menu = QMenu(self.getViewWidget())
        _menu.init_menu(self.legend_menu, self, menu)
        self.connect_triggered_funcs(pos)
        return menu

    def connect_triggered_funcs(self, pos):
        self._connect_func('_edit_legend', self.edit_legend, pos)

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def edit_legend(self, pos):
        dialog = LegendSettingsDialog(self._legend_settings, parent=self.getViewWidget())
        if dialog.exec_():
            settings = dialog.get_result()
            if settings:
                self._legend_settings.update(settings)
                self._apply_settings()

    def _collect_settings(self):
        brush = self.opts.get('brush')
        pen = self.opts.get('pen')

        background_color = QColor(255, 255, 255)
        opacity = 100
        border_color = QColor(100, 100, 100)
        border_width = 1

        if brush is not None:
            color = brush.color()
            background_color = QColor(color)
            opacity = int(round(color.alpha() / 255 * 100))

        if pen is not None:
            border_color = QColor(pen.color())
            if pen.style() == Qt.NoPen or pen.width() <= 0:
                border_width = 0
            else:
                border_width = pen.width()

        return {
            'background_color': background_color,
            'background_opacity': opacity,
            'border_color': border_color,
            'border_width': border_width
        }

    def _apply_settings(self):
        background = QColor(self._legend_settings.get('background_color', QColor(255, 255, 255)))
        opacity_percent = max(0, min(100, int(self._legend_settings.get('background_opacity', 100))))
        if opacity_percent >= 100:
            alpha = 255
        else:
            alpha = int(round(opacity_percent * 2.55))
        background.setAlpha(alpha)
        self.setBrush(pg.mkBrush(background))

        border_color = QColor(self._legend_settings.get('border_color', QColor(100, 100, 100)))
        border_width = max(0, int(self._legend_settings.get('border_width', 1)))
        if border_width == 0:
            pen = pg.mkPen(border_color)
            pen.setStyle(Qt.NoPen)
        else:
            pen = pg.mkPen(border_color, width=border_width)
        self.setPen(pen)


class PlotView(pg.PlotWidget):
    """
    Класс плоскости графика
    """

    APPROXIMATION_MAPPING = {
        'polynomial': np.polynomial.Polynomial,
        'chebyshev': np.polynomial.Chebyshev,
        'legendre': np.polynomial.Legendre
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = None
        self.item = None
        self._prop_dict = {}
        self.ruler = Ruler(self, False)

        self.show_hidden = False
        self.legend_offset = None
        self.default_legend_offset = (50, 50)
        self.left_right_borders = (None, None)

        self.always_show_coordinates = False

        self.textItem = pg.TextItem(color=(0, 0, 0), fill='w')

        self.plotItem.setMenuEnabled(False)  # отключил меню pyqtgraph

        self.plotItem.legend = CustomLegend(offset=self.default_legend_offset, parent=self)
        self.plotItem.legend.setParentItem(self.plotItem.vb)
        self.plotItem.legend.setBrush(pg.mkBrush(255, 255, 255, 255))
        self.plotItem.legend.setPen(pg.mkPen(100, 100, 100))
        self.plotItem.legend.setParentItem(self.plotItem.graphicsItem())

        # Размещаем легенду выше сетки и других элементов графика
        self.plotItem.legend.setZValue(10_000)

        # self.plotItem.getAxis('left').setZValue(0)
        # self.plotItem.getAxis('bottom').setZValue(0)
        # self.plotItem.getViewBox().setZValue(-10)

        self.plotItem.showGrid(x=True, y=True)

        self.create_connections()
        self.available_actions = []

        self._cur_def_color = None

        self.curve_items = []
        self.selected_points = {}

        self.test_nodes = []
        self.constraints = {}
        self.param_constraints = []

        self.plotview_menu = self._load_menu('project', 'plotview')
        self.plotview_toolbar_menu = self._load_menu('project', 'plotview_toolbar')

        self.curves = None

        # Текст для отображения координат
        self.text_item = pg.TextItem("", anchor=(1, 1))
        self.addItem(self.text_item)
        self.proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=600, slot=self.onMouseMoved)
        # self.scene().sigMouseMoved.connect(self.onMouseMoved)

        # Перехватываем событие обновления виджета
        self.plotItem.sigRangeChanged.connect(self.onRangeChanged)

        # Таймер для отложенного обновления
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.setSingleShot(True)
        self.updateTimer.timeout.connect(self.updateSelectedPoints)

        # Переменные для хранения последней позиции мыши и фиксированной оси
        self.last_mouse_scene_pos = None
        self.fixed_axis = None
        self.setMouseTracking(True)

    def onMouseMoved(self, evt):
        modifiers = QApplication.keyboardModifiers()
        pos = evt[0]
        vb = self.plotItem.vb
        mouse_point = vb.mapSceneToView(pos)

        for curve in self.curve_items:

            if self.always_show_coordinates:
                self.text_item.setHtml(
                    f"<div style='text-align: center'><span style='color: black;'>{mouse_point.x():.2f}; {mouse_point.y():.2f}</span></div>")
                self.text_item.setParentItem(self.plotItem)
                self.text_item.setPos(self.lastMousePos)
                self.text_item.show()
            else:
                self.text_item.hide()

            points = curve.scatter.points()
            for i, point in enumerate(points):
                hovered_points = curve.scatter._maskAt(mouse_point)
                if hovered_points[i]:
                    extra_scale = 1
                    if i in self.selected_points[curve]:
                        extra_scale = 1.2
                    if curve.test_node:
                        point.setSize((float(curve.test_node.selected_curve_point_size) + 1) * int(
                            curve.test_node.curve_point_size) * extra_scale)
                    else:
                        point.setSize((float(curve.selected_curve_point_size) + 1) * int(
                            curve.curve_point_size) * extra_scale)
                else:
                    point_index = i
                    if point_index not in self.selected_points[curve]:
                        if curve.test_node:
                            point.setSize(int(curve.test_node.curve_point_size))
                        else:
                            point.setSize(int(curve.curve_point_size))
                    else:
                        if curve.test_node:
                            point.setSize((float(curve.test_node.selected_curve_point_size) + 1) * int(
                                curve.test_node.curve_point_size))
                        else:
                            point.setSize((float(curve.selected_curve_point_size) + 1) * int(
                                curve.curve_point_size))

    def onMouseClicked(self, evt):
        pos = evt.scenePos()
        vb = self.plotItem.vb
        mouse_point = vb.mapSceneToView(pos)
        x_pos = mouse_point.x()
        y_pos = mouse_point.y()

        for curve in self.curve_items:
            points = curve.scatter.points()
            for i, point in enumerate(points):
                point_pos = point.pos()
                hovered_points = curve.scatter._maskAt(mouse_point)
                if hovered_points[i]:
                    # if point_pos.x() - 0.5 < x_pos < point_pos.x() + 0.5 and point_pos.y() - 0.5 < y_pos < point_pos.y() + 0.5:
                    # point_index = (point_pos.x(), point_pos.y())
                    point_index = i
                    if point_index in self.selected_points[curve]:
                        self.selected_points[curve].remove(point_index)
                    else:
                        self.selected_points[curve].add(point_index)
        self.updateSelectedPoints()

    def onRangeChanged(self):
        # Запускаем таймер для отложенного обновления
        self.updateTimer.start(100)

    def updateSelectedPoints(self):
        for curve in self.curve_items:
            points = curve.scatter.points()
            for i, point in enumerate(points):
                point_pos = point.pos()
                # point_index = (point_pos.x(), point_pos.y())
                point_index = i
                if point_index in self.selected_points[curve]:
                    if curve.test_node:
                        point.setSize((float(curve.test_node.selected_curve_point_size) + 1) * int(
                            curve.test_node.curve_point_size))
                        point.setPen(curve.test_node.selected_curve_symbol_color)
                        point.setBrush(
                            pg.mkBrush(QColor(curve.test_node.selected_curve_symbol_fill_color)))
                    else:
                        point.setSize((float(curve.selected_curve_point_size) + 1) * int(
                            curve.curve_point_size))

                        point.setPen(curve.selected_curve_symbol_color)
                        point.setBrush(
                            pg.mkBrush(QColor(curve.selected_curve_symbol_fill_color)))
                    # point.setBrush(pg.mkBrush(255, 0, 0))
                else:
                    if curve.test_node:
                        point.setSize(int(curve.test_node.curve_point_size))
                        if curve.condition_curve:
                            point.setPen(QColor('black'))
                            point.setBrush(
                                pg.mkBrush(QColor(curve.condition_color)))
                        else:
                            point.setPen(curve.test_node.curve_symbol_color)
                            point.setBrush(
                                pg.mkBrush(QColor(curve.test_node.curve_symbol_fill_color)))
                    else:
                        point.setSize(curve.curve_point_size)
                        point.setPen(curve.curve_symbol_color)
                        point.setBrush(
                            pg.mkBrush(QColor(curve.curve_symbol_fill_color)))
                    # point.setBrush(pg.mkBrush(255, 255, 255, 120))

    def set_main_window(self, mw):
        """
        Установка ссылки на главное окно
        """
        self.main_window = mw

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def create_connections(self):
        """Создание привязок сигналов к слотам"""
        self.plotItem.scene().sigMouseHover.connect(self.mouse_hover)
        self.plotItem.scene().sigMouseClicked.connect(self.mouseClicked)  # Нажатия мыши
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def add_custom_curve(self, json_values, approximation=False, interpolation=False, custom=False):
        cc = sp.new_upd_custom_curve((None, self.item._data.project_id, json.dumps(json_values)))
        curve_item = Curve(np.array(json_values['values']), approximation=approximation, interpolation=interpolation,
                           custom=custom, parent=self)
        curve_item.custom_curve_id = cc.id
        curve_item.test_node = None
        curve_item.cc = cc
        self.init_curve(curve_item)
        self.plotItem.legend.addItem(curve_item, json_values['name'])

    def add_approx_curve(self, json_values):
        parent_curve = self.find_curve_by_test_id(json_values['test_id'])
        approximation = False
        interpolation = False
        if 'degree' in json_values:
            cc = self.save_approximation(json_values)
            curve_values = json.loads(cc.values)
            points, extrapolate_func = Curve.build_approximation_values(json_values['type'], json_values['degree'],
                                                                        json_values['extrapolate_forward'],
                                                                        json_values['extrapolate_backward'],
                                                                        parent_curve, self.item.graph_x_multiplier,
                                                                        self.item.graph_x_dultiplier)
            approximation = True
        else:
            points, extrapolate_func = Curve.build_interpolation_values(json_values['type'], parent_curve)
            if points:
                cc = self.save_interpolation(json_values)
                curve_values = json.loads(cc.values)
            else:
                return
            interpolation = True
        curve_item = self._add_custom_curve(curve_values['name'], points, parent_curve, cc.id,
                                            approximation=approximation, interpolation=interpolation)
        curve_item.extrapolation_func = extrapolate_func
        curve_item.cc = cc

    def paste_from_excel(self):
        # Get data from clipboard
        clipboard = QApplication.clipboard()
        data = clipboard.text()

        # Parse data
        try:
            parsed_data = [line.split('\t') for line in data.split('\n') if line]
            curve_name = parsed_data[0][0]
            num_points = int(parsed_data[1][0])
            x_values = [float(excel_to_float(pair[0])) for pair in parsed_data[2:num_points + 2]]
            y_values = [float(excel_to_float(pair[1])) for pair in parsed_data[2:num_points + 2]]

            # Create a new curve with the parsed data
            # self.plot(x_values, y_values, pen='r', name=curve_name)

            values = [(x_values[i], y_values[i]) for i
                      in range(len(x_values))]
            json_values = {'values': values, 'name': curve_name}
            self.add_custom_curve(json_values, custom=True)
        except Exception as e:
            pass

    def mouseClicked(self, ev):
        """
        Левый клик мыши - контекстное меню
        """
        if ev.button() & Qt.RightButton:
            clicked_items = self.plotItem.scene().items(ev.scenePos())
            clicked_curves = {}
            legend = None
            for item in clicked_items:
                if isinstance(item.parentItem(), pg.PlotDataItem):
                    if item.parentItem() not in clicked_curves.keys():
                        clicked_curves[item.parentItem()] = []
                    clicked_curves[item.parentItem()].append(item)
                elif isinstance(item, CustomLegend):
                    legend = item

            if legend:
                pos = legend.mapFromScene(ev.scenePos())
                items = legend.items
                for sample, label in items:
                    if label.sceneBoundingRect().contains(ev.scenePos()) or sample.sceneBoundingRect().contains(
                            ev.scenePos()):
                        sample.item.on_context_menu(pos, True)
                        return
                        # self.showContextMenu(event, label.text)

                legend.on_context_menu(pos)
                return
            for curve in clicked_curves.keys():
                pos = curve.mapFromScene(ev.scenePos())
                if curve.contains(pos):
                    curve.on_context_menu(pos)
                    return
            else:
                self.on_context_menu(ev.scenePos())
        elif ev.button() & Qt.LeftButton:
            pos = ev.scenePos()
            vb = self.plotItem.vb
            mouse_point = vb.mapSceneToView(pos)
            x_pos = mouse_point.x()
            y_pos = mouse_point.y()

            for curve in self.curve_items:
                points = curve.scatter.points()
                for i, point in enumerate(points):
                    point_pos = point.pos()
                    hovered_points = curve.scatter._maskAt(mouse_point)
                    if hovered_points[i]:
                        # if point_pos.x() - 0.5 < x_pos < point_pos.x() + 0.5 and point_pos.y() - 0.5 < y_pos < point_pos.y() + 0.5:
                        # point_index = (point_pos.x(), point_pos.y())
                        point_index = i
                        if point_index in self.selected_points[curve]:
                            self.selected_points[curve].remove(point_index)
                        else:
                            self.selected_points[curve].add(point_index)
            self.updateSelectedPoints()

    def on_context_menu(self, pos):
        menu = self.menu(pos)
        menu.exec_(QCursor.pos())

    def menu(self, pos):
        menu = QMenu(self.getViewWidget())
        _menu.init_menu(self.plotview_menu, self, menu)
        self.connect_triggered_funcs(pos)
        return menu

    def connect_triggered_funcs(self, pos):
        self._connect_func('_paste_curve', self.paste_from_excel)

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def prepare_curves(self, item, sync_with_db=True):
        """
        Строит графики на основе данных из таблицы данных, к которой привязан график.
        :param sync_with_db:
        :param item: объект GraphNode
        :return:
        """
        # Удаляет кривые с графика, если они есть
        self.plotItem.clear()
        self.plotItem.legend.clear()

        self._cur_def_color = None

        if not self.item:
            self.item = item
        self.curves = utils_.collect_project_params(
            sp.get_project_test_params(self.item.parent().parent()._data.project_id))
        self.test_nodes = self.collect_tests()
        # Если у элемента графика заданы смещения легенды, то они иницилизируются
        if hasattr(self.item, 'legend_offset_x') and hasattr(self.item, 'legend_offset_y'):
            self.legend_offset = (self.item.legend_offset_x, self.item.legend_offset_y)
        else:
            self.legend_offset = self.default_legend_offset

        self.plotItem.legend.setOffset(self.legend_offset)

        project_node = self.item.parent().parent()

        # В зависимости от типа графика вызывает нужную функцию для построения
        test_ids = [node._data.id for node in self.test_nodes]
        if item.graph_type == 'xy':
            self.plotItem.legend.setSampleType(GraphCustomSample)
            constraints = json.loads(self.item.graph_constraints)
            self.param_constraints = list(constraints.keys())
            constraints_data = sp.get_x_curves_array(project_node._data.project_id, test_ids,
                                                     self.param_constraints)

            if self.item.graph_label_x in self.curves and self.item.graph_label_y in self.curves:
                x_data = utils_.collect_cell_values(
                    sp.get_x_curves(project_node._data.project_id, test_ids,
                                    self.curves[self.item.graph_label_x].excel_param_name))
                y_data = utils_.collect_cell_values(
                    sp.get_x_curves(project_node._data.project_id, test_ids,
                                    self.curves[self.item.graph_label_y].excel_param_name))
                self._setup_constraint_data(constraints_data)
                self._setup_curves(x_data, y_data)
                self._add_custom_curves()

            self.mark_selected_points()

        elif item.graph_type == 'epure':
            self.plotItem.legend.setSampleType(EpureCustomSample)
            self._prepare_epure_values()

        if self.ruler.enabled:
            self.ruler.add_ruler()
        self.refresh_plane()

    def mark_selected_points(self):
        for curve in self.selected_points:
            self.selected_points[curve] = set()
        graph_folder = self.item.parent()
        if not graph_folder.selected_points:
            return
        try:
            selected = ast.literal_eval(graph_folder.selected_points)
        except:
            return
        for curve in self.curve_items:
            if curve.approximation or curve.interpolation or curve.custom:
                continue
            selected_data = selected.get(curve.test_node._data.project_id, None)
            if not selected_data:
                continue
            for i, point in enumerate(curve.scatter.points()):
                if i in selected_data:
                    self.selected_points[curve].add(i)

        self.updateSelectedPoints()

    def _add_custom_curves(self):
        curves = sp.get_custom_curves(self.item._data.project_id)

        for curve in curves:
            approximation = False
            interpolation = False
            custom = False
            parent_curve = None
            json_values = json.loads(curve.values)
            if 'test_id' in json_values:
                parent_curve = self.find_curve_by_test_id(json_values['test_id'])
                if 'values' not in json_values:
                    if 'degree' not in json_values:
                        json_values['values'], func = Curve.build_interpolation_values(json_values['type'],
                                                                                       parent_curve)
                        interpolation = True
                    else:
                        json_values['values'], func = Curve.build_approximation_values(json_values['type'],
                                                                                       json_values['degree'],
                                                                                       json_values.get(
                                                                                           'extrapolate_forward', None),
                                                                                       json_values.get(
                                                                                           'extrapolate_backward',
                                                                                           None),
                                                                                       parent_curve,
                                                                                       self.item.graph_x_multiplier,
                                                                                       self.item.graph_x_dultiplier)
                        approximation = True
            else:
                custom = True
            if json_values['values']:
                curve_item = self._add_custom_curve(json_values['name'], json_values['values'], parent_curve, curve.id,
                                                    approximation=approximation, interpolation=interpolation,
                                                    custom=custom, _curve_values=curve)

    def _add_custom_curve(self, name, values, parent_curve=None, curve_id=None, approximation=False,
                          interpolation=False, custom=False, _curve_values=None):
        curve_item = Curve(np.array(list(values)), approximation=approximation, interpolation=interpolation,
                           custom=custom, parent=self)
        curve_item.custom_curve_id = curve_id
        if _curve_values is not None:
            curve_item.cc = _curve_values
        if parent_curve:
            curve_item.test_node = parent_curve.test_node
        curve_item.parent_curve = parent_curve
        curve_item.set_curve_name(name)
        self.init_curve(curve_item, iterate_colors=custom)
        self.plotItem.legend.addItem(curve_item, name)
        return curve_item

    @timing_decorator
    def _prepare_epure_values(self):
        import numba
        from collections import defaultdict

        @numba.njit(fastmath=True)
        def filter_values(curve_data, extra_data_values, valid_indices, use_extra_param):
            result = []
            for idx, val in enumerate(curve_data):
                if not use_extra_param or valid_indices[idx]:
                    result.append(val)
            return result

        # Предварительный парсинг
        param_list = ast.literal_eval(self.item.param_list)
        self.epure_curves_dict = {}
        self.extra_param = self.item.extra_param
        self.extra_param_values = set(ast.literal_eval(self.item.extra_param_values))
        project_node = self.item.parent().parent()
        test_ids = [test._data.project_id for test in self.test_nodes]

        # Загрузка данных z_data и _values_list
        z_data = {}
        if self.extra_param:
            z_data = utils_.collect_cell_values(
                sp.get_x_curves(project_node._data.project_id, test_ids, self.extra_param)
            )

        _values_list = sp.get_epure_data(test_ids, param_list)

        # Оптимизированное создание _values_dict
        _values_dict = defaultdict(list)
        for _v in _values_list:
            _values_dict[_v.project_id].append((_v.x_val, _v.y_val))

        count = 0
        for test in self.test_nodes:
            first_curve = None
            project_id = test._data.project_id
            _values = _values_dict.get(project_id, [])

            # Предобработка curves_dict
            curves_dict = defaultdict(list)
            for x_val, y_val in _values:
                curves_dict[x_val].append(to_float(y_val))

            # Преобразуем curves_dict в формат NumPy для ускорения
            for i, (x_val, curve_data) in enumerate(curves_dict.items()):
                curve_data = np.array(curve_data, dtype=np.float32)

                # Оптимизируем фильтрацию значений
                filtered_values = curve_data
                if self.extra_param and (self.extra_param, project_id) in z_data:
                    extra_data = [v.prop_value for v in z_data[self.extra_param, project_id]]
                    valid_indices = np.array(
                        [extra_data[idx] in self.extra_param_values for idx in range(len(extra_data))],
                        dtype=bool
                    )
                    filtered_values = filter_values(curve_data, self.extra_param_values, valid_indices, True)

                if len(filtered_values) == 0:
                    continue

                # Подготовка массивов для кривой
                y = np.arange(len(filtered_values), dtype=np.float32)
                if self.item.oy_list and ast.literal_eval(self.item.oy_list):
                    oy_list = np.array(ast.literal_eval(self.item.oy_list)[:len(filtered_values)], dtype=np.float32)
                    curve_item = Curve(np.column_stack((filtered_values, oy_list)), epure_points=True, parent=self)
                else:
                    curve_item = Curve(np.column_stack((filtered_values, y)), epure_points=True, parent=self)

                curve_item.test_node = test
                self.init_curve(curve_item, iterate_colors=(first_curve is None))

                # Интерполяция
                if len(filtered_values) > 2:
                    linear_y = np.linspace(y.min(), y.max(), 100, dtype=np.float32)
                    cubic_interp = interp1d(y, filtered_values, kind='quadratic', assume_sorted=True)
                    points = np.column_stack((cubic_interp(linear_y), linear_y))
                    curve_item = Curve(points, epure=True, parent=self)
                else:
                    curve_item = Curve(np.column_stack((filtered_values, y)), epure=True, parent=self)

                curve_item.test_node = test
                self.init_curve(curve_item, iterate_colors=(first_curve is None))

                # Добавление в легенду
                project_curve_name = test.curve_name if test.curve_name else test.name
                if first_curve is None:
                    first_curve = curve_item
                    self.plotItem.legend.addItem(curve_item, project_curve_name)

                count += 1

        print(count)

    @timing_decorator
    def _prepare_epure_values(self):
        def is_valid(extra_data, j):
            for i in range(len(extra_data)):
                if extra_data[i] in self.extra_param_values and j == i:
                    return True
            return False

        param_list = ast.literal_eval(self.item.param_list)
        self.epure_curves_dict = {}
        self.extra_param = self.item.extra_param
        self.extra_param_values = ast.literal_eval(self.item.extra_param_values)
        project_node = self.item.parent().parent()
        test_ids = [test._data.project_id for test in self.test_nodes]
        if self.extra_param:
            z_data = utils.collect_cell_values(
                sp.get_x_curves(project_node._data.project_id, test_ids,
                                self.extra_param))
        else:
            z_data = {}

        _values_list = sp.get_epure_data(test_ids, param_list)
        _values_dict = {}

        for _v in _values_list:
            if _v.project_id not in _values_dict:
                _values_dict[_v.project_id] = []
            _values_dict[_v.project_id].append(_v)
        count = 0
        for test in self.test_nodes:
            first_curve = None
            _values = _values_dict.get(test._data.project_id, [])
            curves_dict = {x_val: [obj.y_val for obj in _values if obj.x_val == x_val] for x_val, _ in
                           [(obj.x_val, None) for obj in _values]}
            for i, (curve, curve_data) in enumerate(curves_dict.items()):
                count += 1
                _cd = [to_float(v) for v in curve_data]
                filtered_values = []
                if self.extra_param and (self.extra_param, test._data.project_id) in z_data:
                    if is_valid([v.prop_value for v in z_data[self.extra_param, test._data.project_id]], i):
                        filtered_values = _cd
                else:
                    filtered_values = _cd

                if len(filtered_values) == 0:
                    continue

                x = np.array(filtered_values)
                if self.item.oy_list is not None and ast.literal_eval(self.item.oy_list):
                    oy_list = ast.literal_eval(self.item.oy_list)[:len(filtered_values)]
                    curve_item = Curve(np.array([(num, to_float(oy_list[i])) for i, num in enumerate(filtered_values)]),
                                       epure_points=True, parent=self)
                    y = [to_float(i) for i in range(len(oy_list))]
                else:
                    curve_item = Curve(np.array([(num, i) for i, num in enumerate(filtered_values)]), epure_points=True,
                                       parent=self)
                    y = [i for i in range(len(filtered_values))]
                curve_item.test_node = test
                self.init_curve(curve_item, iterate_colors=False if first_curve else True)

                if len(filtered_values) > 2:
                    # Интерполяция
                    linear_y = np.linspace(min(y), max(y), 100)
                    cubic_interp = interp1d(y, x, kind='quadratic')
                    points = list(zip(cubic_interp(linear_y), linear_y))
                    curve_item = Curve(np.array(points),
                                       epure=True, parent=self)
                else:
                    if self.item.oy_list is not None and ast.literal_eval(self.item.oy_list):
                        oy_list = ast.literal_eval(self.item.oy_list)[:len(filtered_values)]
                        curve_item = Curve(
                            np.array([(num, to_float(oy_list[i])) for i, num in enumerate(filtered_values)]),
                            epure=True, parent=self)
                    else:
                        curve_item = Curve(np.array([(num, i) for i, num in enumerate(filtered_values)]),
                                           epure=True, parent=self)

                curve_item.test_node = test
                self.init_curve(curve_item, iterate_colors=False if first_curve else True)
                project_curve_name = None
                project_name = None
                if test.curve_name:
                    project_curve_name = test.curve_name
                else:
                    project_name = test.name
                if first_curve is None:
                    first_curve = curve_item
                    self.plotItem.legend.addItem(curve_item, project_curve_name if project_curve_name else project_name)
        print(count)

    def get_next_default_color(self):
        color = self._cur_def_color
        _def_colors = [
            'green',
            'yellow',
            'red',
            'blue',
            'purple'
        ]
        if color:
            self._cur_def_color = _def_colors[(_def_colors.index(color) + 1) % len(_def_colors)]
        else:
            self._cur_def_color = _def_colors[0]
        return self._cur_def_color

    def refresh_linked_curves(self, test_node):
        for curve in self.plotItem.items:
            if curve.test_node == test_node:
                curve.init_style()

    def collect_tests(self):
        test_folder = \
            [child for child in self.item.parent().parent().children if child.internal_type() == 'product_folder'][0]
        return self._inspect_children(test_folder, False)

    def _inspect_children(self, root, root_deleted):
        test_nodes = []
        for child in root.children:
            if child.internal_type() == 'test':
                if hasattr(child._data, 'deleted') and (
                        child._data.deleted == 'False' or child._data.deleted is False) and root_deleted is False:
                    test_nodes.append(child)
            else:
                if root_deleted:
                    test_nodes += self._inspect_children(child, True)
                elif child._data.deleted is True:
                    test_nodes += self._inspect_children(child, True)
                else:
                    test_nodes += self._inspect_children(child, False)
        return test_nodes

    def _find_parent_item(self, test, type_):
        parent = test.parent()
        while parent.internal_type() != 'product_folder':
            if parent.internal_type() == type_:
                return parent
            parent = parent.parent()
        return None

    def _setup_constraint_data(self, constraints_data):
        class ParamConstraint:
            def __init__(self, name, test_id, min_val, max_val):
                self.name = name
                self.test_id = test_id
                self.x_data = []
                self.min_val = min_val
                self.max_val = max_val
                self.cformula = False

            def is_valid(self, i):
                if not self.x_data[i].replace('.', '', 1).isdigit():
                    return True
                if self.min_val <= float(self.x_data[i]) <= self.max_val:
                    return True
                return False

        self.constraints = {}
        constr = json.loads(self.item.graph_constraints)
        for data in constraints_data:
            if (data.project_id, data.excel_param_name) not in self.constraints.keys():
                cns = ParamConstraint(data.excel_param_name, data.project_id, constr[data.excel_param_name]['min'],
                                      constr[data.excel_param_name]['max'])
                if data.param_prop_name == 'cformula':
                    cns.cformula = True
                self.constraints[(data.project_id, data.excel_param_name)] = cns

            cns = self.constraints[(data.project_id, data.excel_param_name)]
            if cns.cformula is True and data.param_prop_name == 'value':
                continue
            if cns.cformula is False and data.param_prop_name == 'cformula':
                cns.cformula = True
                cns.x_data.clear()
            cns.x_data.append(data.prop_value)

    def check_x_val_constraint(self, i, project_id):
        params = self.param_constraints
        for param in params:
            if (project_id, param) in self.constraints.keys():
                if not self.constraints[(project_id, param)].is_valid(i):
                    return False
        return True

    def _setup_curves(self, x_data, y_data):
        test_nodes = self.test_nodes
        test_ids = {test._data.project_id: test for test in test_nodes}
        curves = self.sort_curves(test_ids, x_data, y_data)

        for _, curve in curves.items():
            curve_test = curve.test_node
            if curve_test.display_as_curve == 'True' or curve_test.display_as_curve is True:
                condition_curves = {}
                values = []
                if curve_test.use_conditions == 'True' and curve_test.conditions and curve_test.conditions != '[]':
                    self.filter_by_conditions(curve, condition_curves)

                else:
                    if curve_test.use_conditions == 'True':
                        curve_test.use_conditions = 'False'
                    values = self.filter_by_constraints(curve)
                for key, _curve in condition_curves.items():
                    self._add_curve(_curve.values, curve_test, _curve.brush, _curve.symbol,
                                    _curve.point_size, _curve.curve_name, condition_curve=True)
                if values:
                    self._add_curve(values, curve_test)

    @timing_decorator
    def sort_curves(self, test_ids, x_data, y_data):
        class _Curve:
            def __init__(self):
                self.x_data = []
                self.y_data = []
                self.curve_name = None
                self.test_node = None

        curves = {}

        x_param = self.item.graph_label_x
        y_param = self.item.graph_label_y
        for test_id, test in test_ids.items():
            if (x_param, test_id) in x_data and (y_param, test_id) in y_data:
                _x = x_data[(x_param, test_id)]
                _y = y_data[(y_param, test_id)]
                curve = _Curve()
                curves[test_id] = curve
                curve.test_node = test

                curves[test_id].x_data = _x
                curves[test_id].y_data = _y
        return curves

    def filter_by_constraints(self, curve):
        return [(curve.x_data[i], curve.y_data[i]) for i in range(len(curve.x_data)) if
                self.check_x_val_constraint(i, curve.test_node._data.project_id) and curve.x_data[
                    i].prop_value is not None and curve.y_data[i].prop_value is not None]

    def filter_by_conditions(self, curve, condition_curves):
        class ConditionCurve:
            def __init__(self, brush, symbol, point_size, curve_name):
                self.brush = brush
                self.symbol = symbol
                self.point_size = point_size
                self.curve_name = curve_name
                self.values = []

        project_node = self.item.parent().parent()
        curve_test = curve.test_node
        conditions = ast.literal_eval(curve_test.conditions)
        if conditions[0]['x'] not in self.curves:
            return None
        condition_dict = {to_float(c['val']): c for c in conditions}
        z_data = utils_.collect_cell_values(
            sp.get_x_curves(project_node._data.project_id, [curve_test._data.project_id],
                            self.curves[conditions[0]['x']].excel_param_name))
        _z = z_data[self.curves[conditions[0]['x']].excel_param_name, curve_test._data.project_id]
        for i in range(len(curve.x_data)):
            if _z[i].prop_value is None or curve.x_data[i].prop_value is None or curve.y_data[
                i].prop_value is None:
                continue
            z = to_float(_z[i].prop_value)
            exists_in_cond = False
            existing_num = None
            for num in condition_dict:
                if compare_floats(z, num):
                    exists_in_cond = True
                    existing_num = num
                    break
            if exists_in_cond:
                c = condition_dict[existing_num]
                if (c['color'], c['type'], c['point_size']) not in condition_curves:
                    condition_curves[(c['color'], c['type'], c['point_size'])] = ConditionCurve(c['color'],
                                                                                                c['type'],
                                                                                                c[
                                                                                                    'point_size'],
                                                                                                c['name'])

                condition_curves[(c['color'], c['type'], c['point_size'])].values.append(
                    (curve.x_data[i], curve.y_data[i]))

    def _add_curve(self, values, curve_test, brush=None, symbol=None, point_size=None, legend_name=None,
                   condition_curve=False):
        if brush:
            curve_test.curve_color = brush
        if symbol:
            curve_test.curve_point_symbol = symbol
        if point_size:
            curve_test.curve_point_size = point_size

        group_by_items = set()
        curve_item = Curve(values, parent=self)
        curve_item.condition_curve = condition_curve

        if condition_curve:
            curve_item.condition_color = brush

        curve_item.test_node = curve_test
        if legend_name is None:
            curve_name = curve_item.test_node.curve_name if curve_item.test_node.curve_name else curve_item.test_node.name
        else:
            curve_name = legend_name
        curve_item.set_curve_name(curve_name)

        if self.item.graph_group_by:
            group_by_item = self._find_parent_item(curve_item.test_node, self.item.graph_group_by)
            if group_by_item:
                if group_by_item and group_by_item not in group_by_items:
                    group_by_items.add(group_by_item)
                    curve_item.group_by_item = group_by_item
                    self.plotItem.legend.addItem(curve_item, group_by_item.data())
                    self.init_curve(curve_item)
        else:
            self.plotItem.legend.addItem(curve_item, curve_name)
            self.init_curve(curve_item)

    def find_curve_by_test_id(self, test_id):
        for item in self.plotItem.items:
            if hasattr(item, 'test_node') and item.test_node is not None:
                if item.test_node._data.project_id == test_id:
                    return item

    def save_interpolation(self, json_values):
        cc = sp.new_upd_custom_curve((None, self.item._data.project_id, json.dumps(json_values)))
        return cc

    def save_approximation(self, json_values):
        cc = sp.new_upd_custom_curve((None, self.item._data.project_id, json.dumps(json_values)))
        return cc

    def add_interpolation(self, curve_values):
        type_ = curve_values['type']
        test_id = curve_values['test_id']
        name = curve_values['name']
        # extrapolate_forward = curve_values['extrapolate_forward']
        # extrapolate_backward = curve_values['extrapolate_backward']

        parent_curve = self.find_curve_by_test_id(test_id)
        if parent_curve is None:
            return

        x = parent_curve.xData

        # if extrapolate_backward is not None:
        #     x = [extrapolate_backward] + x
        # if extrapolate_forward is not None:
        #     x = x + [extrapolate_forward]

        y = parent_curve.yData

        linear_x = np.linspace(x.min(), x.max(), 100)
        try:
            cubic_interp = interp1d(x, y, kind=type_)
            points = zip(linear_x, cubic_interp(linear_x))
        except Exception as e:
            basic_funcs.error('Ошибка', 'Не хватает данных для построения интерполяции \n Расшифровка: ' + str(e))
            print(e)
            return

        # cc = sp.new_upd_custom_curve((None, self.item._data.project_id, json.dumps(curve)))

        return points, cubic_interp

    def add_approximation(self, curve):
        type_ = curve['type']
        test_id = curve['test_id']
        name = curve['name']
        degree = curve['degree']
        extrapolate_forward = curve['extrapolate_forward']
        extrapolate_backward = curve['extrapolate_backward']

        parent_curve = self.find_curve_by_test_id(test_id)
        if parent_curve is None:
            return
        min_x = min(parent_curve.xData) if extrapolate_forward is None else float(extrapolate_forward)
        max_x = max(parent_curve.xData) if extrapolate_backward is None else float(extrapolate_backward)

        if type_ == 'polynomial':
            cls = np.polynomial.Polynomial
        elif type_ == 'chebyshev':
            cls = np.polynomial.Chebyshev
        elif type_ == 'legendre':
            cls = np.polynomial.Legendre
        else:
            return None
        try:
            polynomial_ = cls.fit(x=parent_curve.xData, y=parent_curve.yData, deg=degree)
            polynomial = cls(polynomial_.coef, domain=[min_x, max_x])
        except:
            basic_funcs.error('Ошибка', 'Линия является прямой')
            return

        # cc = sp.new_upd_custom_curve((None, self.item._data.project_id, json.dumps(curve)))

        x_values = np.linspace(min_x, max_x, 100)
        points = zip(x_values, polynomial(x_values))

        return points, polynomial

    def init_curve(self, curve, iterate_colors=False):
        """
        Добавление кривой на плоскость графика.
        :param curve: Кривая Curve
        :return:
        """
        if curve not in self.plotItem.items:
            self.plotItem.addItem(curve)
            self.curve_items.append(curve)
            self.selected_points[curve] = set()
        if self.item.graph_type == 'xy':
            curve.init_style(iterate_colors=iterate_colors)
        elif self.item.graph_type == 'epure':
            curve.init_style(iterate_colors=iterate_colors)

    def refresh_curve(self, item):
        """
        Обновление одной кривой
        """
        # Берем все свойства объекта, ищем нужную кривую и обновляем свойства
        new_props = vars(item)
        for _item in self.plotItem.items:
            if isinstance(_item, Curve) and _item.curve_id == item._data.id:
                curve = _item
                curve.update_class_props(new_props)
                curve.init_style()
                break

    def refresh(self, index=None, sync_with_db=True):
        """
        Обновление кривой
        :param index: объект, который нужно обновить (сейчас не используется)
        :param sync_with_db:
        :return:
        """
        self.prepare_curves(self.item)

    def set_axis_step(self, axis: str, major: float = None, minor: float = None):
        """Установка шага сетки по осям."""
        self.plotItem.getAxis(axis).setTickSpacing(major=None if major == 0 else major,
                                                   minor=None if minor == 0 else minor)

    @property
    def view_box(self) -> pg.ViewBox:
        return self.plotItem.vb

    @classmethod
    def valid_range(cls, range_) -> bool:
        """Проверяет что переданный диапазон инициализирован и не содержит None элементов."""
        if range_ == [0, 0]:
            return False
        return all(r is not None for r in range_)

    def refresh_plane(self):
        plot_item = self.plotItem
        plot_item.setTitle(f'<span style="font-size: 14pt;">{self.item.graph_name}</span>')  # Заголовок графика

        if self.item.graph_x_comment:
            x_label = self.item.graph_label_x + ', ' + self.item.graph_x_comment
        else:
            x_label = self.item.graph_label_x

        if self.item.graph_y_comment:
            y_label = self.item.graph_label_y + ', ' + self.item.graph_y_comment
        else:
            y_label = self.item.graph_label_y

        plot_item.setLabel(axis='left', text=y_label)  # Подпись вертикальной ось
        plot_item.setLabel(axis='bottom', text=x_label)  # Подпись горизонтальной оси

        # plot_item.showGrid(x=True, y=True, alpha=self.item.graph_grid_size)  # Толщина линий сетки

        def get_steps(x, y):
            x = to_float(x)
            y = to_float(y)
            if x == 0 and y == 0:
                return 0, 0
            if x == 0 and y != 0:
                return y, y
            if x != 0 and y == 0:
                return x, x

            return x, y

        if not to_bool(self.item.graph_x_step_auto):
            x, y = get_steps(self.item.graph_x_major_step, self.item.graph_x_minor_step)
            self.set_axis_step('bottom', x,
                               y)  # Шаг сетки по Х
        else:
            self.set_axis_step('bottom', None, None)
        if not to_bool(self.item.graph_y_step_auto):
            x, y = get_steps(self.item.graph_y_major_step, self.item.graph_y_minor_step)
            self.set_axis_step('left', x, y)
        else:
            self.set_axis_step('left', None, None)

        self.view_box.setMouseEnabled(x=not to_bool(self.item.graph_fixed_x), y=not to_bool(self.item.graph_fixed_y))

        # Если текущий диапазон графика невалидный(первое построение) - применить автомасштабирование
        range_x = [None if not self.item.graph_left_x else to_float(self.item.graph_left_x),
                   None if not self.item.graph_right_x else to_float(self.item.graph_right_x)]
        range_y = [None if not self.item.graph_bottom_y else to_float(self.item.graph_bottom_y),
                   None if not self.item.graph_top_y else to_float(self.item.graph_top_y)]

        if not self.valid_range(range_x) and not self.valid_range(range_y):
            self.auto_scale()
        else:  # Выставляем диапазон из объекта БД
            if self.valid_range(range_x):
                plot_item.setRange(xRange=range_x, padding=0)
            if self.valid_range(range_y):
                plot_item.setRange(yRange=range_y, padding=0)

    def auto_scale(self):
        """Функция автоматического масшабиования графической области"""
        x_range = []
        y_range = []
        for plot in self.plotItem.dataItems:
            if isinstance(plot, Curve):
                if plot.xData is None and plot.yData is None:
                    continue
                if plot.xData.all() and plot.yData.all():
                    x_range.append(plot.xData)
                    y_range.append(plot.yData)
        if x_range and y_range:
            self.plotItem.setRange(
                xRange=list(chain(*x_range)),
                yRange=list(chain(*y_range)),
                padding=0.01,
            )

    def update_legend_pos(self):
        """
        Сохранение положения легенды в БД
        """
        if self.plotItem.legend.current_pos is None:
            return

        # В качестве шаблона берем основное свойство и копируем во временные переменные
        graph_prop = self.item._data
        graph_prop_lox = copy(graph_prop)
        graph_prop_loy = copy(graph_prop)

        # Меняем в них название свойства и значение
        graph_prop_lox.project_prop = 'legend_offset_x'
        graph_prop_lox.project_prop_value = str(self.plotItem.legend.current_pos.x())

        graph_prop_loy.project_prop = 'legend_offset_y'
        graph_prop_loy.project_prop_value = str(self.plotItem.legend.current_pos.y())

        # Сохраняем в бд
        new_props = sp.new_update_project_from_record_array(
            [graph_prop_lox.table_fit(PROJECT_TABLE), graph_prop_loy.table_fit(PROJECT_TABLE)])

        if new_props:
            self.item.update_class_props(
                new_props)  # обновление свойств у элемента графика в дереве на основе полученных из бд

    def mouse_hover(self, items: list):
        """Обработка наведения мышки на объект"""
        pos = self.plotItem.vb.mapSceneToView(self.lastMousePos)
        plotItem = self.plotItem
        curves = [item for item in plotItem.items if isinstance(item, Curve)]
        curve_points = tuple(
            (item, item.scatter.pointsAt(pos))
            for item in curves if item.scatter in items
        )

        if not curve_points:
            self.textItem.hide()
            return

        if html := self._plot_coord_table(curve_points):
            self.textItem.show()
            self.textItem.setHtml(html)
            self.textItem.setParentItem(self.plotItem)
            self.textItem.setPos(self.lastMousePos)
        else:
            self.textItem.hide()

    def _plot_coord_table(self, curve_points: "Iterable[Tuple[CurveItem, List[pg.SpotItem]]]",
                          color: str = "#000000") -> str:
        """Таблица с координатами графика в формате HTML"""
        tables = []

        for curve, points in curve_points:
            accuracy = '{:.' + '3' + 'f}'
            rows = tuple(
                f"<tr><td>{accuracy.format(point.pos().x())}</td><td>{accuracy.format(point.pos().y())}</td></tr>"
                for point in points
            )
            if curve.test_node is not None:
                if curve.condition_curve:
                    hex_color = pg.mkColor(curve.condition_color).name()
                else:
                    hex_color = pg.mkColor(QColor(curve.test_node.curve_symbol_fill_color)).name()
            else:
                hex_color = pg.mkColor(curve.curve_symbol_fill_color).name()

            rgba_color = list(pg.mkColor(hex_color).getRgb())  # Get RGB values
            rgba_color[-1] = 0.5

            if rows:  # Генерируем заголовок только если мышь наведена на точки
                tables.append(f"""
                <table border="1"
style="background-color: rgba({','.join([str(v) for v in rgba_color])});">
                <tr><th>{curve.scatter.name()}</th></tr>
                </table>
                <table border="1" style="background-color: rgba({','.join([str(v) for v in rgba_color])});">
                <tr><th>{self.item.graph_label_x}</th><th>{self.item.graph_label_y}</th></tr>
                {''.join(rows)}
                </table>
                """)
            else:
                pass

        if len(tables) == 0:
            return ""
        elif len(tables) == 1:
            return tables[0]

        return f"""
        <table>
        <tr>{''.join(f"<td>{table}</td>" for table in tables)}</tr>
        </table>
        """

    def update_selected_points(self):
        selected_points = {}
        for curve in self.selected_points:
            if not curve.approximation and not curve.interpolation and not curve.custom and self.selected_points[curve]:
                selected_points[curve.test_node._data.project_id] = self.selected_points[curve]

        graph_folder_prop = copy(self.item.parent()._data)
        graph_folder_prop.project_prop = 'selected_points'
        graph_folder_prop.project_prop_value = str(selected_points)

        # Сохраняем в бд
        new_props = sp.new_update_project_from_record(graph_folder_prop.table_fit(PROJECT_TABLE))

        if new_props:
            self.item.parent().update_class_props([
                new_props])  # обновление свойств у элемента графика в дереве на основе полученных из бд

            self.item.parent().selected_points = new_props.prop_value

    def update_curve_name_in_legend(self, curve, new_name):
        for item in self.plotItem.legend.items:
            # item[0] - это GraphicsWidget, содержащий метку легенды
            # item[1] - это сама кривуля
            if item[0].item == curve:
                # Устанавливаем новое имя
                item[1].setText(new_name)
                # Также обновляем имя кривой
                curve.opts['name'] = new_name
                break

    def commit_changes(self):
        """
        Здесь писать все изменения, которые нужно выполнить при закрытии вкладки
        """
        self.update_selected_points()
        self.update_legend_pos()

        view = self.parent().parent().index.model().view

        for child_tab in view.get_opened_tabs():
            if hasattr(child_tab, 'plot_page'):
                child_tab.plot_page.plotView.mark_selected_points()


class Curve(pg.PlotDataItem):
    """
    Кривая, которая отображается на графике.
    """
    Missing = 0  # Иное нажатие
    Curve = 1  # Нажатие на кривую
    Point = 2  # Нажатие на точку

    LINE_STYLES = [
        (Qt.NoPen, 'Прозрачная'),
        (Qt.SolidLine, 'Линия'),
        (Qt.DashLine, 'Пунктирная линия'),
        (Qt.DotLine, 'Линия из точек'),
        (Qt.DashDotLine, 'Линия точка-тире'),
        (Qt.DashDotDotLine, 'Линия точка-точка-тире'),
    ]

    def __init__(self, values, approximation=False, interpolation=False, custom=False, epure=False, epure_points=False,
                 parent=None):
        self.extrapolation_func = None
        self.cc = None
        self.parent = parent
        self.custom_curve_id = None
        self.approximation = approximation
        self.interpolation = interpolation
        self.custom = custom
        self.epure_points = epure_points
        self.epure = epure
        self.condition_curve = False
        self.epure = epure
        self.points = self.setup_points(values)
        self.values = values
        self.cur_values = copy(values)
        self.condition_color = None

        super().__init__(np.array(self.points))
        self._props = None

        self.parent_curve = None

        self.test_node = None
        self.group_by_item = None

        self.x_data = []
        self.y_data = []

        # Основные свойства ячейки
        self.curve_color = None
        self.curve_width = None
        self.curve_point_symbol = None
        self.curve_is_visible = None
        self.curve_point_size = None
        self.curve_line_style = None
        self.curve_name = None
        self.curve_id = None

        self.curve_symbol_color = 'black'
        self.curve_symbol_fill_color = 'red'

        self.selected_curve_point_size = 0.5
        self.selected_curve_symbol_color = 'black'
        self.selected_curve_symbol_fill_color = 'red'

        self.curve_param_name = None

        self.extrapolate_forward = None
        self.extrapolate_backward = None

        # Доступные действия для таблицы
        self.available_actions = []

        self.highlighted_points = []

        # Загрузка меню для элементов
        self.point_menu = [m for m in self._load_menu('project', 'curve_point') if m.name != '_broken']
        self.curve_menu = self._load_menu('project', 'curve')

        curve_menu = []
        for m in self.curve_menu:
            if m.name == '_customize_curve':
                if not (self.approximation or self.interpolation):
                    curve_menu.append(m)
            elif m.name == '_approximate' or m.name == '_interpolate':
                if not (self.approximation or self.interpolation or self.custom):
                    curve_menu.append(m)
            elif m.name == '_extrapolate':
                if self.approximation:
                    curve_menu.append(m)
            elif m.name == '_ruler_mark':
                if self.approximation or self.interpolation:
                    curve_menu.append(m)
            elif m.name == '_remove':
                if self.approximation or self.interpolation or self.custom:
                    curve_menu.append(m)
            else:
                curve_menu.append(m)

        self.curve_menu = curve_menu

        # self.curve_menu = [m for m in self.curve_menu if m.name != '_remove' and m.name != '_ruler_mark']

        self.enumerate_point_menu()

        self.textItem = pg.TextItem(color=(0, 0, 0), fill='w')  # без понятия что это и зачем

    def setup_points(self, points):
        if self.approximation or self.interpolation or self.custom or self.epure or self.epure_points:
            return points
        values = [(to_float(c[0].prop_value), to_float(c[1].prop_value)) for c in points]
        return self.apply_multipliers(values)

    def apply_multipliers(self, values):
        return [(x * float(self.parent.item.graph_x_multiplier) / float(self.parent.item.graph_x_dultiplier),
                 y * float(self.parent.item.graph_y_multiplier) / float(self.parent.item.graph_y_dultiplier))
                for x, y in values]

    def remove_multipliers(self, values):
        return [(x / float(self.parent.item.graph_x_multiplier) * float(self.parent.item.graph_x_dultiplier),
                 y / float(self.parent.item.graph_y_multiplier) * float(self.parent.item.graph_y_dultiplier))
                for x, y in values]

    def enumerate_point_menu(self):
        for p in self.point_menu:
            p.init_order += 100

    # def on_point_clicked(self, scatter, points):
    #     for point in points:
    #         index = list(scatter.points()).index(point)
    #         custom_point = self.points[index]
    #         print(f"clicked {index}")

    def approximate(self, pos):
        """Функция для аппроксимации"""
        dialog = ApproxDialog(self.scatter.name(), parent=self.getViewWidget())
        if dialog.exec_() == QInputDialog.Accepted:
            name, poly_type, degree, extrapolate_forward, extrapolate_backward = dialog.get_result()
            cls = self.parent.APPROXIMATION_MAPPING.get(poly_type, None)

            json_values = {
                'name': name,
                'test_id': self.test_node._data.project_id,
                'type': poly_type,
                'extrapolate_forward': extrapolate_forward,
                'extrapolate_backward': extrapolate_backward
            }
            if cls is not None:
                json_values['degree'] = degree
            self.parent.add_approx_curve(json_values)

    def update_class_props(self, props: dict):
        for prop, value in props.items():
            if prop:
                setattr(self, prop, value)

    def _load_menu(self, mode, location):
        menu = sp.get_user_menu_(mode, location)
        self.available_actions += [action.name for action in menu]
        return menu

    def update_props(self, props: dict):
        for prop in self._props:
            if prop.prop_name in props.keys():
                prop.prop_value = props[prop.prop_name]
                setattr(self, prop.prop_name, prop.prop_value)
        self.init_style()

    def init_props(self, props):
        # Инициализация свойств объектов из бд
        self._props = props
        for prop in props:
            if prop.prop_name == 'name':
                prop.prop_name = 'curve_name'
            if prop.prop_value:
                setattr(self, prop.prop_name, prop.prop_value)
                if not self.curve_id:
                    self.curve_id = prop.id

    def init_style(self, iterate_colors=False):
        # Инициализация стиля кривой. Если свойства не заданы, используются по умолчанию
        if self.approximation or self.epure or self.interpolation:
            self.setSymbol(None)
            self.setPen(color=QColor(self.test_node.curve_color),
                        width=2,
                        style=self.LINE_STYLES[
                            1][
                            0])
        else:
            if self.test_node:
                self.setSymbol(self.test_node.curve_point_symbol)
                self.setSymbolSize(int(self.test_node.curve_point_size))

                if self.epure_points:
                    self.setPen(color=QColor(self.test_node.curve_color),
                                width=2,
                                style=self.LINE_STYLES[
                                    0][
                                    0])
                else:
                    self.setPen(color=QColor(self.test_node.curve_color),
                                width=int(self.test_node.curve_width),
                                style=self.LINE_STYLES[
                                    int(self.test_node.curve_line_style) if not self.epure else 1][
                                    0])
                if not self.condition_curve:
                    self.setSymbolPen(QColor(self.test_node.curve_symbol_color))
                    self.setSymbolBrush(
                        pg.mkBrush(QColor(self.test_node.curve_symbol_fill_color)))
                else:
                    self.setSymbolPen(QColor('black'))
                    self.setSymbolBrush(
                        pg.mkBrush(QColor(self.condition_color)))
            else:
                if isinstance(self.cc.values, str):
                    self.cc.values = json.loads(self.cc.values)
                values = self.cc.values
                self.setSymbol(values.get('curve_point_symbol', 'o'))
                self.setSymbolSize(int(values.get('curve_point_size', 3)))
                self.setPen(color=QColor(values.get('curve_color', 'blue')),
                            width=int(values.get('curve_width', 1)),
                            style=self.LINE_STYLES[
                                int(values.get('curve_line_style', 1)) if not self.epure else 1][
                                0])
                self.setSymbolPen(QColor(values.get('curve_symbol_color', 'black')))
                self.setSymbolBrush(
                    pg.mkBrush(QColor(values.get('curve_symbol_fill_color', 'blue'))))

                self.curve_point_size = int(values.get('curve_point_size', 10))
                self.curve_symbol_color = values.get('curve_symbol_color', 'black')
                self.curve_symbol_fill_color = values.get('curve_symbol_fill_color', 'blue')
                self.curve_color = values.get('curve_color', 'blue')

    def set_curve_name(self, name):
        self.curve.setData(name=name)
        self.scatter.setData(name=name)

    def on_context_menu(self, pos, ignore_contains=False):
        menu = self.menu(pos, ignore_contains)
        menu.exec_(QCursor.pos())

    def menu(self, pos, ignore_contains=False):
        menu = QMenu(self.getViewWidget())
        if ignore_contains:
            _menu.init_menu(self.curve_menu, self, menu)
        else:
            if type_ := self.contains(pos):
                if type_ == self.Point:
                    _menu.init_menu(self.curve_menu + self.point_menu, self, menu)
                else:
                    _menu.init_menu(self.curve_menu, self, menu)
        self.connect_triggered_funcs(pos)
        return menu

    def connect_triggered_funcs(self, pos):
        # self._connect_func('_broken', self.set_broken, pos)
        self._connect_func('_ruler_mark', self.set_ruler_mark, pos)
        self._connect_func('_copy_curve', self.copy_curve, pos)
        self._connect_func('_paste_curve', self.paste_curve, pos)
        self._connect_func('_approximate', self.approximate, pos)
        self._connect_func('_interpolate', self.interpolate, pos)
        self._connect_func('_extrapolate', self.extrapolate, pos)
        self._connect_func('_remove', self.remove_self, pos)
        self._connect_func('_customize_curve', self.customize, pos)

    def customize(self, pos):
        dialog = EditLineDialog(self.test_node if self.test_node else self.cc)
        if dialog.exec_() == QInputDialog.Accepted:
            self.init_style(False)
            if dialog.res:
                self.cc = dialog.get_result()
                name = json.loads(self.cc.values)['name']
                self.parent.update_curve_name_in_legend(self, name)
                # self.set_curve_name(name)
            else:
                self.parent.refresh_linked_curves(self.test_node)

    def extrapolate(self, pos):
        if isinstance(self.cc.values, str):
            cc_values = json.loads(self.cc.values)
        else:
            cc_values = self.cc.values
        dialog = ExtrapolationDialog(cc_values['extrapolate_forward'], cc_values['extrapolate_backward'],
                                     min(self.xData), max(self.xData), cc_values.get('off', True),
                                     parent=self.getViewWidget())
        if dialog.exec_() == QInputDialog.Accepted:
            cc_values['extrapolate_forward'], cc_values['extrapolate_backward'], cc_values['off'] = dialog.get_result()
            self.cc.values = cc_values

            sp.new_upd_custom_curve((self.cc.id, self.cc.graph_project_id, json.dumps(self.cc.values)))

            values, _ = self.build_approximation_values(cc_values['type'],
                                                        cc_values['degree'],
                                                        cc_values.get(
                                                            'extrapolate_forward', None) if cc_values.get('off',
                                                                                                          True) else None,
                                                        cc_values.get(
                                                            'extrapolate_backward', None) if cc_values.get('off',
                                                                                                           True) else None,
                                                        self.parent_curve, self.parent.item.graph_x_multiplier,
                                                        self.parent.item.graph_x_dultiplier)

            self.setData(np.array(list(values)))

    def interpolate(self, pos):
        """Функция для аппроксимации"""
        dialog = InterpDialog(self.scatter.name(), parent=self.getViewWidget())
        if dialog.exec_() == QInputDialog.Accepted:
            name, poly_type = dialog.get_result()
            cls = self.parent.APPROXIMATION_MAPPING.get(poly_type, None)

            json_values = {
                'name': name,
                'test_id': self.test_node._data.project_id,
                'type': poly_type,
            }
            self.parent.add_approx_curve(json_values)

    @staticmethod
    def build_interpolation_values(type_, parent_curve):
        if parent_curve is None:
            return None, None

        x = parent_curve.xData
        y = parent_curve.yData

        linear_x = np.linspace(x.min(), x.max(), 100)
        try:
            cubic_interp = interp1d(x, y, kind=type_)
            points = zip(linear_x, cubic_interp(linear_x))
        except Exception as e:
            basic_funcs.error('Ошибка', 'Не хватает данных для построения интерполяции \n Расшифровка: ' + str(e))
            print(e)
            return None, None

        return points, cubic_interp

    @staticmethod
    def build_approximation_values(type_, degree, extrapolate_forward, extrapolate_backward, parent_curve, x_mul,
                                   x_dul):
        if parent_curve is None:
            return None, None
        min_x = min(parent_curve.xData) if extrapolate_backward is None else float(extrapolate_backward) * float(
            x_mul) / float(x_dul)
        max_x = max(parent_curve.xData) if extrapolate_forward is None else float(extrapolate_forward) * float(
            x_mul) / float(x_dul)

        if type_ == 'polynomial':
            cls = np.polynomial.Polynomial
        elif type_ == 'chebyshev':
            cls = np.polynomial.Chebyshev
        elif type_ == 'legendre':
            cls = np.polynomial.Legendre
        else:
            return None, None
        try:
            polynomial_ = cls.fit(x=parent_curve.xData, y=parent_curve.yData, deg=degree)
            polynomial = cls(polynomial_.coef, domain=[min_x, max_x])
        except:
            basic_funcs.error('Ошибка', 'Линия является прямой')
            return None, None

        x_values = np.linspace(min_x, max_x, 100)
        points = zip(x_values, polynomial(x_values))

        return points, polynomial

    def remove_self(self, pos):
        if self.custom_curve_id:
            res = sp.remove_custom_curve(self.custom_curve_id)
            if res:
                self.parent.plotItem.removeItem(self)

    def copy_curve(self, pos):
        # Get the data points of the curve

        if not self.approximation or not self.interpolation:
            curve_data = self.getData()

            data_header = f"Dep1D_CD\n{len(curve_data[0])}\n"

            data_to_copy = "\n".join(
                ["{}\t{}".format(float_to_excel(x), float_to_excel(y)) for x, y in zip(*curve_data)])

            # Copy data to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(data_header + data_to_copy)
        else:
            graph_folder = self.parent.item.parent()
            test_ids = [self.test_node._data.project_id]
            param_list = [self.parent.item.graph_label_x] + [graph.graph_label_y for graph in graph_folder.children if
                                                             not graph._data.deleted and graph.graph_label_x == self.parent.item.graph_label_x]
            project_node = self.parent.item.parent().parent()
            curves = utils_.collect_cell_values(
                sp.get_x_curves_array(project_node._data.project_id, test_ids, param_list))
            vals = {name: [to_float(_.prop_value) for _ in values] for name, values in curves.items()}
            headers = [_[0] for _ in vals.keys()]
            x_data = vals[self.parent.item.graph_label_x, self.test_node._data.project_id]
            min_x = min(x_data)
            max_x = max(x_data)
            x_values = np.linspace(min_x, max_x, 100)
            if isinstance(self.cc.values, str):
                curve_values = json.loads(self.cc.values)
            else:
                curve_values = self.cc.values

            if curve_values['type'] == 'polynomial':
                cls = np.polynomial.Polynomial
            elif curve_values['type'] == 'chebyshev':
                cls = np.polynomial.Chebyshev
            elif curve_values['type'] == 'legendre':
                cls = np.polynomial.Legendre
            else:
                return None, None

            y_datas = []

            for y_vals in vals.values():
                _x = [_ for i, _ in enumerate(x_data) if y_vals[i] is not None and _ is not None]
                _y = [_ for i, _ in enumerate(y_vals) if x_data[i] is not None and _ is not None]
                try:
                    polynomial_ = cls.fit(x=_x, y=_y, deg=curve_values['degree'])
                    polynomial = cls(polynomial_.coef, domain=[min_x, max_x])
                except:
                    basic_funcs.error('Ошибка', 'Линия является прямой')
                    return None, None
                y_datas.append(polynomial(x_values))

            data_to_copy = []
            for i in range(len(y_datas[0])):
                row = []
                for j in range(len(headers)):
                    row.append(str(y_datas[j][i]))
                data_to_copy.append('\t'.join(row))

            clipboard = QApplication.clipboard()
            clipboard.setText('\t'.join(headers) + '\n' + '\n'.join(data_to_copy))

    def paste_curve(self, pos):
        self.parent.paste_from_excel()

    def set_ruler_mark(self, pos):
        if self.approximation or self.interpolation:
            self.parent.ruler.set_pos(pos, self)
        # self.parent.ruler.set_visible(True)

    def set_broken(self, pos):
        def guess_index(v):
            i = 0
            for p in self.values:
                if v == p:
                    return i
                if p in self.cur_values:
                    i += 1

        # self.parent.main_window.show_notification(
        #     f'Помечание точек битыми в графике в данный момент на стадии переработки.')
        points = self.scatter.pointsAt(pos)
        if len(points) == 1:
            point = points[0]
            point_index = point.index()
            p = self.cur_values[point_index]
            if p in self.cur_values:
                self.cur_values.remove(p)
            else:
                self.cur_values.insert(guess_index(p), p)
            self.setData(np.array(self.setup_points(self.cur_values)))

    def _connect_func(self, action_name, func, *args):
        """Связывает действие и функцию, принимает название действия, функцию и переменный набор аргументов после нее"""
        if action_name in self.available_actions and hasattr(self, action_name):
            getattr(self, action_name).triggered.connect(lambda: func(*args))

    def contains(self, pos):
        if any(self.scatter.pointsAt(pos)):
            return self.Point
        elif self.curve.mouseShape().contains(pos):
            return self.Curve
        else:
            return self.Missing
