from PySide2.QtCore import Qt, QPointF
from PySide2.QtWidgets import QMenu
from PySide2.QtGui import QCursor
import pyqtgraph as pg
from typing import Any, List, Tuple, Optional
from functools import partial
import json
import numpy as np
import logging

from app.plugins.project.services.data_processors.plot_dp import PlotProcessor
from app.plugins.project.services.extrapolation import ExtrapolationService
from app.plugins.project.visualization.views.plot_views.menu_tools.plot_menu_actions import PlotMenuActions, \
    ActionTarget, get_available_actions
from app.plugins.project.visualization.views.plot_views.menu_tools.curve_clipboard import CurveClipboard
from db import sp
from app.menu_service import get_menu
from app.plugins.project.dialogs.create_approx import ApproxDialog
from app.plugins.project.dialogs.create_interpolation import InterpDialog
from app.plugins.project.dialogs.extrapolation_dialog import ExtrapolationDialog
from app.plugins.project.dialogs.edit_line import EditLineDialog, visual_style_to_dialog_style
from app.plugins.project.utils_ import invalidate_project_param_cache_after_update

logger = logging.getLogger(__name__)


class PlotContextMenuMixin:
    """Миксин для обработки контекстного меню графика"""

    plotItem: Any
    curve_items: list
    data_processor: PlotProcessor
    remove_custom_curve: callable  # Ссылка на метод PlotDataMixin

    def __init__(self):
        self.proxy_context = self.init_proxy_for_context_menu()

        self.action_states = {
            'grid': False,
            'legend': False,
            'curve_visibility': {}
        }

        # Загружаем доступные действия из БД при инициализации
        self._cache_available_actions()
        self._load_menus()
        self._sync_initial_states()

    def _cache_available_actions(self):
        """Кэширует доступные действия из базы данных"""
        curve_actions = get_menu('project', 'curve')
        point_actions = get_menu('project', 'point')
        plot_actions = get_menu('project', 'plot')

        self.available_action_names = {
            ActionTarget.CURVE: {action.name for action in get_available_actions(curve_actions)},
            ActionTarget.POINT: {action.name for action in get_available_actions(point_actions)},
            ActionTarget.PLOT: {action.name for action in get_available_actions(plot_actions)}
        }

    def _load_menus(self):
        """Загружает конфигурации меню"""
        # Фильтруем все возможные действия по доступным из БД
        all_actions = PlotMenuActions.get_all_actions()

        self.curve_menu = [
            action for action in all_actions
            if action.target == ActionTarget.CURVE
               and action.name in self.available_action_names[ActionTarget.CURVE]
        ]

        self.point_menu = [
            action for action in all_actions
            if action.target == ActionTarget.POINT
               and action.name in self.available_action_names[ActionTarget.POINT]
        ]

        self.plot_menu = [
            action for action in all_actions
            if action.target == ActionTarget.PLOT
               and action.name in self.available_action_names[ActionTarget.PLOT]
        ]

    def init_proxy_for_context_menu(self):
        return pg.SignalProxy(
            self.scene().sigMouseClicked,
            rateLimit=60,
            slot=self.onContextMenuRequested
        )

    def onContextMenuRequested(self, evt):
        """Обрабатывает запрос на показ контекстного меню"""
        if evt[0].button() != Qt.RightButton:
            return

        # Проверяем, не произошел ли клик по легенде
        pos = evt[0].scenePos()
        if hasattr(self.plotItem, 'legend') and self.plotItem.legend:
            legend = self.plotItem.legend
            for sample, label in legend.items:
                if label.sceneBoundingRect().contains(pos):
                    # Если клик по элементу легенды - прерываем обработку
                    return

            legend_rect = legend.mapRectToScene(legend.boundingRect())
            if legend_rect.contains(pos):
                # Если клик по фону легенды - прерываем обработку
                return

        mouse_point = self.plotItem.vb.mapSceneToView(pos)

        # Создаем меню в зависимости от места клика
        menu = self.create_context_menu(mouse_point)
        if menu:
            menu.exec_(QCursor.pos())

    def create_context_menu(self, pos: QPointF) -> Optional[QMenu]:
        """Создает контекстное меню в зависимости от позиции"""
        menu = QMenu(self)

        # Проверяем клик по точке
        clicked_points = self._find_points_at_position(pos)
        if clicked_points:
            self._add_point_specific_actions(menu, clicked_points)
            menu.addSeparator()
            self._add_curve_specific_actions(menu, curve=clicked_points[0][0])
            return menu

        # Проверяем клик по кривой
        clicked_curve = self._find_curve_at_position(pos)
        if clicked_curve:
            self._add_curve_specific_actions(menu, curve=clicked_curve)
            return menu

        # Если не попали ни по точке, ни по кривой - это клик по графику
        self._add_plot_specific_actions(menu)
        return menu if not menu.isEmpty() else None

    def _find_curve_at_position(self, pos: QPointF) -> Optional[Any]:
        """Находит кривую под курсором мыши"""
        for curve in self.curve_items:
            if not curve.isVisible():
                continue

            # Получаем ближайшую точку на кривой
            point_index = self._find_nearest_point_index(curve, pos)
            if point_index is not None:
                # Проверяем, находится ли точка достаточно близко (в пределах 5 пикселей)
                screen_pos = self.plotItem.vb.mapViewToScene(pos)
                data_point = QPointF(curve.xData[point_index], curve.yData[point_index])
                screen_point = self.plotItem.vb.mapViewToScene(data_point)

                if (screen_pos - screen_point).manhattanLength() < 5:
                    return curve
        return None

    def _find_nearest_point_index(self, curve: Any, pos: QPointF) -> Optional[int]:
        """Находит индекс ближайшей точки на кривой"""
        if len(curve.xData) == 0:
            return None

        # Находим ближайшую точку по X
        x = pos.x()
        nearest_idx = min(range(len(curve.xData)),
                          key=lambda i: abs(curve.xData[i] - x))
        return nearest_idx

    def _add_point_specific_actions(self, menu: QMenu, points: List[Tuple[Any, int]]):
        """Добавляет действия специфичные для точек"""
        for curve, point_idx in points:
            x = curve.xData[point_idx]
            y = curve.yData[point_idx]

            point_submenu = menu.addMenu(f"Точка на кривой '{curve.name()}' ({x:.2f}, {y:.2f})")

            for action in self.point_menu:
                if action == "|":
                    point_submenu.addSeparator()
                    continue

                qa = point_submenu.addAction(action.translation)
                qa.setCheckable(action.is_checkable)
                data = {'curve': curve, 'point_idx': point_idx, 'action': action.name}
                qa.triggered.connect(partial(self._handle_point_action, data))

    def _add_curve_specific_actions(self, menu: QMenu, curve=None):
        """Добавляет действия специфичные для кривых"""
        for action in self.curve_menu:
            qa = menu.addAction(action.translation)
            qa.setCheckable(action.is_checkable)

            if action.name == PlotMenuActions.CURVE_HIDE.name and curve:
                curve_name = curve.name()
                is_visible = curve.isVisible()
                self.action_states['curve_visibility'][curve_name] = is_visible
                qa.setChecked(not is_visible)

            if action.icon:
                qa.setIcon(action.icon)
            if action.shortcut:
                qa.setShortcut(action.shortcut)

            # Сохраняем данные в свойствах QAction
            qa.setProperty('action_name', action.name)
            qa.setProperty('curve', curve)
            # Используем метод класса напрямую
            qa.triggered.connect(self._on_curve_action_triggered)

    def _add_plot_specific_actions(self, menu: QMenu):
        """Добавляет действия специфичные для графика"""
        clipboard_available = CurveClipboard.can_paste()

        for action in self.plot_menu:
            if action.name == PlotMenuActions.PLOT_PASTE.name and not clipboard_available:
                continue
            qa = menu.addAction(action.translation)
            qa.setCheckable(action.is_checkable)

            # Устанавливаем состояние чекбокса из текущего состояния
            if action.name == PlotMenuActions.PLOT_GRID.name:
                qa.setChecked(self.action_states['grid'])
            elif action.name == PlotMenuActions.PLOT_LEGEND.name:
                qa.setChecked(self.action_states['legend'])

            if action.icon:
                qa.setIcon(action.icon)
            if action.shortcut:
                qa.setShortcut(action.shortcut)

            # Сохраняем действие в свойстве QAction
            qa.setProperty('action_name', action.name)
            # Используем метод класса напрямую
            qa.triggered.connect(self._on_plot_action_triggered)

        if hasattr(self, 'remove_ruler'):
            menu.addSeparator()
            remove_active = menu.addAction("Убрать активную линейку")
            remove_active.setEnabled(getattr(self, 'active_ruler_id', None) is not None)
            remove_active.triggered.connect(lambda _checked=False: self.remove_ruler())
            remove_all = menu.addAction("Убрать все линейки")
            remove_all.setEnabled(bool(getattr(self, 'rulers', {})))
            remove_all.triggered.connect(lambda _checked=False: self.remove_all_rulers())

    def _handle_point_action(self, data: dict, checked: bool = False):
        """Обработчик действий для точек"""
        print(f"Point action triggered: {data}, checked={checked}")
        curve = data['curve']
        point_idx = data['point_idx']
        action_name = data['action']
        print(f"Point action: {action_name} for point {point_idx} on curve {curve.name()}")

    def _handle_curve_action(self, data: dict, checked: bool = False):
        """Обработчик действий для кривых"""
        curve = data['curve']
        action_name = data['action']

        if action_name == PlotMenuActions.CURVE_HIDE.name and curve:
            # Получаем test_id для кривой
            test_id = self.data_processor.get_test_id_for_curve(curve)
            if test_id:
                # Получаем все кривые для этого test_id
                related_curves = self.data_processor.get_curves_for_test(test_id)
                # Скрываем/показываем все связанные кривые
                for related_curve in related_curves:
                    curve_name = related_curve.name()
                    self.action_states['curve_visibility'][curve_name] = not checked
                    related_curve.setVisible(not checked)
            else:
                # Если test_id не найден, скрываем только текущую кривую
                curve_name = curve.name()
                self.action_states['curve_visibility'][curve_name] = not checked
                curve.setVisible(not checked)

            # Обновляем легенду
            if hasattr(self.plotItem, 'legend') and self.plotItem.legend is not None:
                for sample, label in self.plotItem.legend.items:
                    if label.text == curve.name():
                        sample.update()

        elif action_name == PlotMenuActions.CURVE_STYLE.name:
            self._customize_curve_style(curve)

        elif action_name == PlotMenuActions.CURVE_COPY.name and curve:
            project_id = getattr(getattr(self.data_processor, 'data_manager', None), 'project_id', None)
            CurveClipboard.copy_curve(curve, project_id=project_id)

        elif action_name == PlotMenuActions.CURVE_APPROXIMATION.name and curve:
            # Получаем test_id для кривой
            test_id = self.data_processor.get_test_id_for_curve(curve)
            dialog = ApproxDialog(f"Approximation_{curve.name()}", self, test_id=test_id)
            if dialog.exec_():
                data = dialog.get_result()
                result = json.loads(data)
                self.add_approximated_curve(
                    source_curve=curve,
                    degree=result['degree'],
                    name=result['name'],
                    color=result['color'],
                    line_width=result['line_width']
                )

        elif action_name == PlotMenuActions.CURVE_INTERPOLATION.name and curve:
            # Получаем test_id для кривой
            test_id = self.data_processor.get_test_id_for_curve(curve)
            dialog = InterpDialog(f"Interpolation_{curve.name()}", self, test_id=test_id)
            if dialog.exec_():
                data = dialog.get_result()
                result = json.loads(data)
                self.add_interpolated_curve(
                    source_curve=curve,
                    kind=result['type'],
                    name=result['name'],
                    color=result['color'],
                    line_width=result['line_width']
                )

        elif action_name == PlotMenuActions.CURVE_EXTRAPOLATION.name and curve:
            x_data = curve.xData
            dialog = ExtrapolationDialog(
                forward=max(x_data),
                backward=min(x_data),
                min_x=min(x_data),
                max_x=max(x_data),
                off=False,
                parent=self
            )
            if dialog.exec_():
                forward, backward, is_enabled = dialog.get_result()
                if is_enabled:
                    sorted_x = np.sort(np.asarray(x_data))
                    if sorted_x.size == 0:
                        return

                    diffs = np.diff(sorted_x)
                    valid_diffs = diffs[~np.isclose(diffs, 0.0)]
                    x_step = float(np.median(valid_diffs)) if valid_diffs.size else 0.0

                    if np.isclose(x_step, 0.0):
                        x_step = 1.0

                    min_x = float(sorted_x[0])
                    max_x = float(sorted_x[-1])

                    forward_value = float(forward)
                    backward_value = float(backward)

                    left_span = max(0.0, min_x - backward_value)
                    right_span = max(0.0, forward_value - max_x)

                    left_points = int(np.ceil(left_span / x_step)) if left_span > 0 else 0
                    right_points = int(np.ceil(right_span / x_step)) if right_span > 0 else 0

                    max_points_per_side = getattr(ExtrapolationService, 'MAX_POINTS_PER_SIDE', 10000)

                    if left_span > 0 and left_points == 0:
                        left_points = 1
                    if right_span > 0 and right_points == 0:
                        right_points = 1

                    left_points = min(left_points, max_points_per_side)
                    right_points = min(right_points, max_points_per_side)

                    try:
                        self.add_extrapolated_curve(
                            source_curve=curve,
                            left_points=left_points,
                            right_points=right_points,
                            degree=2,
                            name=f"Extrapolation_{curve.name()}",
                            left_limit=backward_value,
                            right_limit=forward_value,
                        )
                    except Exception:
                        logger.exception("Could not build extrapolation for curve %r", curve.name())
                    
        elif action_name == PlotMenuActions.CURVE_DELETE.name and curve:
            # Проверяем, что кривая является пользовательской или сгенерированной (аппр./интерп./экстрап.)
            generated_type = getattr(curve, 'generated_curve_type', None)
            has_custom_id = getattr(curve, 'custom_curve_id', None) is not None

            if has_custom_id or generated_type in {'approximation', 'interpolation', 'extrapolation'}:
                # Удаляем кривую с графика (и из БД, если нужно)
                result = self.remove_custom_curve(curve)
                if not result:
                    print(f"Не удалось удалить кривую {curve.name()}")
            else:
                print(f"Кривая {curve.name()} не является пользовательской и не может быть удалена")
                
        elif action_name == PlotMenuActions.CURVE_RULER_MARK.name and curve:
            # Получаем текущую позицию курсора
            cursor_pos = self.lastMousePos
            if cursor_pos:
                vb = self.plotItem.vb
                view_pos = vb.mapSceneToView(cursor_pos)
                # Проверяем, что миксин линейки инициализирован
                if hasattr(self, 'set_ruler_mark'):
                    # Устанавливаем метку линейки
                    # Если зажат Ctrl, создаем новую линейку
                    #new_ruler = action.modifiers() & Qt.ControlModifier
                    new_ruler = False
                    if new_ruler:
                        # Для нового формата с несколькими линейками
                        if hasattr(self, 'create_ruler'):
                            # Создаем новую линейку
                            new_ruler_id = self.create_ruler()
                            self.set_ruler_mark(view_pos.x(), curve, new_ruler_id)
                            print(f"Создана новая линейка {new_ruler_id} для кривой {curve.name() if hasattr(curve, 'name') else 'без имени'}")
                        else:
                            # Для старого формата - просто вызываем обычный метод
                            self.set_ruler_mark(view_pos.x(), curve)
                    else:
                        # Используем активную линейку
                        self.set_ruler_mark(view_pos.x(), curve)
                else:
                    print("Линейка не инициализирована должным образом")

        print(f"Curve action: {action_name}, checked: {checked}, curve: {curve.name() if curve else 'all curves'}")

    def _customize_curve_style(self, curve):
        """Open the style editor and apply its result without rebuilding the plot."""
        if curve is None or not hasattr(curve, 'apply_style'):
            logger.warning("Cannot customize a missing or invalid curve")
            return
        try:
            dialog = EditLineDialog(curve, parent=self)
            if not dialog.exec_() or not dialog.result_style:
                return
            old_name = curve.name() if callable(getattr(curve, 'name', None)) else ''
            style = getattr(curve, 'style_config', None)
            if not isinstance(style, dict):
                curve._style_config = {}
                style = curve._style_config
            style.update(dialog.result_style)
            new_name = style.get('name')
            if new_name and hasattr(curve, 'setName'):
                curve.setName(new_name)
            elif new_name and isinstance(getattr(curve, 'opts', None), dict):
                curve.opts['name'] = new_name
            curve.apply_style()
            self._persist_curve_style(curve, dialog.result_style)
            if hasattr(self.plotItem, 'legend') and self.plotItem.legend is not None:
                for sample, label in self.plotItem.legend.items:
                    if getattr(label, 'text', None) == old_name and new_name:
                        label.setText(new_name)
                self.plotItem.legend.update()
            curve.update()
        except Exception:
            logger.exception("Could not customize curve style")

    def _persist_curve_style(self, curve, style):
        """Persist custom curves; Project/Test curves retain their existing node mechanism."""
        custom_id = getattr(curve, 'custom_curve_id', None)
        if custom_id is None:
            self._persist_project_curve_style(curve, style)
            return
        records = getattr(self.data_processor, 'other_data', ())
        record = next((item for item in records if getattr(item, 'id', None) == custom_id), None)
        if record is None:
            logger.warning("Custom curve %r no longer exists; style is session-only", custom_id)
            return
        try:
            values = json.loads(record.values) if isinstance(record.values, str) else dict(record.values or {})
            stored_style = values.get('style')
            if not isinstance(stored_style, dict):
                stored_style = {}
            stored_style.update(style)
            values['style'] = stored_style
            values['name'] = style.get('name', values.get('name', ''))
            values['color'] = style.get('color', values.get('color'))
            values['line_width'] = style.get('width', values.get('line_width'))
            record.values = json.dumps(values)
            sp.new_upd_custom_curve((record.id, record.graph_project_id, record.values))
        except Exception:
            logger.exception("Could not persist custom curve %r", custom_id)

    def _persist_project_curve_style(self, curve, style):
        curve_map = getattr(self.data_processor, 'curve_map', {})
        test_nodes = getattr(self.data_processor, 'test_nodes', {})
        test_key = next((key for key, item in curve_map.items() if item is curve), None)
        node = test_nodes.get(test_key)
        data = getattr(node, '_data', None)
        if data is None:
            logger.debug("Generated curve %r has no persistent ProjectData node", curve)
            return
        legacy_style = visual_style_to_dialog_style(style, style.get('name', ''))
        props = [
            (None, data.id, data.id_up, 7, key, str(value), None, None, None, 0, None)
            for key, value in legacy_style.items()
        ]
        try:
            updated_props = sp.new_update_project_from_record_array(props)
            if hasattr(node, 'update_class_props'):
                node.update_class_props(updated_props)
            invalidate_project_param_cache_after_update(item_id=getattr(data, 'id', None), item=node, data=data)
        except Exception:
            logger.exception("Could not persist ProjectData curve style")

    def _handle_plot_action(self, action_name: str, checked: bool = False):
        """Обработчик действий для графика"""
        if action_name == PlotMenuActions.PLOT_PASTE.name:
            self._paste_curve_from_clipboard()

        elif action_name == PlotMenuActions.PLOT_GRID.name:
            self.action_states['grid'] = checked
            self.plotItem.showGrid(checked, checked, alpha=0.3)
            if hasattr(self.plotItem, 'ctrl') and hasattr(self.plotItem.ctrl, 'gridCheck'):
                self.plotItem.ctrl.gridCheck.setChecked(checked)

        elif action_name == PlotMenuActions.PLOT_LEGEND.name:
            self.action_states['legend'] = checked
            # Создаем легенду, если её ещё нет
            if not hasattr(self.plotItem, 'legend') or self.plotItem.legend is None:
                self.init_legend()
            # Просто скрываем/показываем легенду
            self.plotItem.legend.setVisible(checked)

        elif action_name == PlotMenuActions.PLOT_RESET_VIEW.name:
            self.plotItem.getViewBox().autoRange()

    def _paste_curve_from_clipboard(self):
        """Вставляет кривую из буфера обмена."""

        clipboard_curve = CurveClipboard.peek()
        if clipboard_curve is None or not clipboard_curve.points:
            return

        base_name = clipboard_curve.name or "Вставленная кривая"
        curve_name = self._generate_unique_curve_name(base_name)

        points = list(clipboard_curve.points)
        x_values, y_values = zip(*points)

        style = clipboard_curve.style.copy()
        style['name'] = curve_name

        metadata = clipboard_curve.metadata.copy()
        metadata.setdefault('source', metadata.get('source', 'clipboard'))
        metadata.setdefault('original_name', clipboard_curve.metadata.get('copied_from', clipboard_curve.name))
        metadata.setdefault('project_id', getattr(getattr(self.data_processor, 'data_manager', None), 'project_id', None))

        custom_curve_id = self.data_processor.save_manual_curve(curve_name, points, style.copy(), metadata)
        if not custom_curve_id:
            return

        new_curve = self.add_curve(x_values, y_values, **style)
        new_curve.custom_curve_id = custom_curve_id

    def _generate_unique_curve_name(self, base_name: str) -> str:
        """Создает уникальное имя для вставляемой кривой."""

        if not base_name:
            base_name = "Вставленная кривая"

        existing_names = {curve.name() for curve in self.curve_items if hasattr(curve, 'name')}
        if base_name not in existing_names:
            return base_name

        copy_name = f"{base_name} (копия)"
        if copy_name not in existing_names:
            return copy_name

        counter = 2
        while True:
            candidate = f"{base_name} (копия {counter})"
            if candidate not in existing_names:
                return candidate
            counter += 1

    # Добавляем методы для сохранения/загрузки состояний
    def save_states(self):
        """Сохраняет текущие состояния в настройки"""
        # Здесь можно добавить сохранение в QSettings или другое хранилище
        pass

    def load_states(self):
        """Загружает сохраненные состояния из настроек"""
        # Здесь можно добавить загрузку из QSettings или другого хранилища
        pass

    class MenuAction:
        """Вспомогательный класс для описания действий меню"""

        def __init__(self, name, translation, is_checkable=False):
            self.name = name
            self.translation = translation
            self.is_checkable = is_checkable

    def _find_points_at_position(self, mouse_point: QPointF) -> List[Tuple[Any, int]]:
        """Находит точки под курсором мыши"""
        clicked_points = []

        for curve in self.curve_items:
            if not curve.isVisible() or not hasattr(curve, 'scatter') or curve.scatter is None:
                continue

            points = curve.scatter.points()
            clicked_mask = curve.scatter._maskAt(mouse_point)

            for i, (point, is_clicked) in enumerate(zip(points, clicked_mask)):
                if is_clicked:
                    clicked_points.append((curve, i))

        return clicked_points

    def _sync_initial_states(self):
        """Синхронизация начального состояния с текущим состоянием виджета"""
        # Инициализируем сетку
        self.action_states['grid'] = True
        self.plotItem.showGrid(True, True, alpha=0.3)
        if hasattr(self.plotItem, 'ctrl') and hasattr(self.plotItem.ctrl, 'gridCheck'):
            self.plotItem.ctrl.gridCheck.setChecked(True)

        # Инициализируем легенду
        if not hasattr(self.plotItem, 'legend') or self.plotItem.legend is None:
            self.init_legend()
        self.action_states['legend'] = True
        self.plotItem.legend.setVisible(True)
        
        # Добавляем обработку кликов по легенде
        if hasattr(self.plotItem, 'legend'):
            self.plotItem.legend.scene().sigMouseClicked.connect(self._handle_legend_click)

        # Синхронизируем состояние видимости кривых
        for curve in self.curve_items:
            if hasattr(curve, 'name'):
                self.action_states['curve_visibility'][curve.name()] = curve.isVisible()

    def _handle_legend_click(self, event):
        """Обработчик клика по легенде"""
        if event.button() != Qt.RightButton:
            return

        # Получаем элемент легенды, по которому кликнули
        pos = event.scenePos()
        legend = self.plotItem.legend
        
        # Проходим по всем элементам легенды
        for sample, label in legend.items:
            if label.sceneBoundingRect().contains(pos):
                # Находим соответствующую кривую
                curve = next((c for c in self.curve_items if c.name() == label.text), None)
                if curve:
                    menu = self._create_legend_context_menu(curve)
                    menu.exec_(QCursor.pos())
                    event.accept()
                return

        legend_rect = legend.mapRectToScene(legend.boundingRect())
        if not legend_rect.contains(pos):
            return

        # Если клик по фону легенды, показываем меню настроек легенды
        menu = self._create_legend_context_menu()
        if not menu.isEmpty():
            menu.exec_(QCursor.pos())
            event.accept()

    def _create_legend_context_menu(self, curve=None) -> QMenu:
        menu = QMenu(self)

        if curve is not None:
            self._add_curve_specific_actions(menu, curve=curve)
            if not menu.isEmpty():
                menu.addSeparator()

        if hasattr(self.plotItem, 'legend') and self.plotItem.legend is not None:
            action = menu.addAction("Настройка легенды…")
            action.triggered.connect(self.plotItem.legend.open_settings_dialog)

        return menu

    def _on_plot_action_triggered(self, checked):
        """Обработчик сигнала triggered для действий графика"""
        action = self.sender()  # получаем QAction, который вызвал сигнал
        action_name = action.property('action_name')
        self._handle_plot_action(action_name, checked)

    def _on_curve_action_triggered(self, checked):
        """Обработчик сигнала triggered для действий кривой"""
        action = self.sender()  # получаем QAction, который вызвал сигнал
        data = {
            'action': action.property('action_name'),
            'curve': action.property('curve')
        }
        self._handle_curve_action(data, checked)
