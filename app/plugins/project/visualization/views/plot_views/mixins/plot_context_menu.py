from PySide2.QtCore import Qt, QPointF
from PySide2.QtWidgets import QMenu
from PySide2.QtGui import QCursor
import pyqtgraph as pg
from typing import Any, List, Tuple, Optional
from functools import partial
import json
import numpy as np

from app.plugins.project.services.data_processors.plot_dp import PlotProcessor
from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.visualization.views.plot_views.menu_tools.plot_menu_actions import PlotMenuActions, \
    ActionTarget, get_available_actions
from app.plugins.project.visualization.views.plot_views.menu_tools.curve_clipboard import CurveClipboard
from db import sp
from app.plugins.project.dialogs.create_approx import ApproxDialog
from app.plugins.project.dialogs.create_interpolation import InterpDialog
from app.plugins.project.dialogs.extrapolation_dialog import ExtrapolationDialog
from app.plugins.project.dialogs.curve_style import CurveStyleDialog


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
        curve_actions = sp.get_user_menu_('project', 'curve')
        point_actions = sp.get_user_menu_('project', 'point')
        plot_actions = sp.get_user_menu_('project', 'plot')

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

        elif action_name == PlotMenuActions.CURVE_COPY.name and curve:
            project_id = getattr(getattr(self.data_processor, 'data_manager', None), 'project_id', None)
            CurveClipboard.copy_curve(curve, project_id=project_id)

        elif action_name == PlotMenuActions.CURVE_STYLE.name and curve:
            self._show_curve_style_dialog(curve)

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

                    self.add_extrapolated_curve(
                        source_curve=curve,
                        left_points=left_points,
                        right_points=right_points,
                        degree=2,
                        name=f"Extrapolation_{curve.name()}",
                        left_limit=backward_value,
                        right_limit=forward_value,
                    )
                    
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

    def _show_curve_style_dialog(self, curve):
        """Отображает диалог настройки стиля кривой и применяет изменения"""

        dialog = CurveStyleDialog(curve.style, parent=self)
        if not dialog.exec_():
            return

        new_style = dialog.get_style()
        if not isinstance(new_style, dict):
            return

        self._apply_curve_style(curve, new_style)
        self._persist_curve_style(curve)

    def _apply_curve_style(self, curve, style):
        """Применяет стиль к кривой и обновляет легенду"""

        old_style = curve.style.copy()
        for key in ('color', 'line_style', 'width', 'symbol', 'symbol_size', 'symbol_color', 'fill_color'):
            if key in style:
                curve.style_config[key] = style[key]

        # Если раньше цвета маркера совпадали с цветом линии, обновляем их
        if 'color' in style:
            new_color = style['color']
            if old_style.get('symbol_color') == old_style.get('color'):
                curve.style_config['symbol_color'] = new_color
            if old_style.get('fill_color', old_style.get('symbol_color')) == old_style.get('color'):
                curve.style_config['fill_color'] = new_color

        curve.apply_style()
        self._update_legend_item(curve)

    def _update_legend_item(self, curve):
        if hasattr(self.plotItem, 'legend') and self.plotItem.legend is not None:
            for sample, label in self.plotItem.legend.items:
                if getattr(sample, 'item', None) == curve:
                    sample.update()
                    break

    def _persist_curve_style(self, curve):
        """Сохраняет стиль кривой в БД и в связанных данных."""

        applied_style = curve.style.copy()

        curve_id = self._extract_custom_curve_id(curve, applied_style)
        if curve_id is not None:
            if self._persist_custom_curve_style(curve_id, applied_style):
                return

        test_id = self.data_processor.get_test_id_for_curve(curve)
        if test_id is not None:
            self._persist_test_curve_style(test_id, applied_style)

    def _extract_custom_curve_id(self, curve, style):
        curve_id = getattr(curve, 'custom_curve_id', None)
        if curve_id is None and isinstance(style, dict):
            curve_id = style.get('custom_curve_id')

        if curve_id is None:
            return None

        try:
            normalized_id = int(curve_id)
        except (TypeError, ValueError):
            normalized_id = curve_id

        if getattr(curve, 'custom_curve_id', None) != normalized_id:
            curve.custom_curve_id = normalized_id

        if isinstance(style, dict):
            style['custom_curve_id'] = normalized_id

        return normalized_id

    def _get_cached_custom_curve(self, curve_id):
        def matches(candidate):
            candidate_id = getattr(candidate, 'id', None)
            try:
                return int(candidate_id) == int(curve_id)
            except (TypeError, ValueError):
                return candidate_id == curve_id

        other_data = getattr(self.data_processor, 'other_data', []) or []
        for item in other_data:
            if matches(item):
                return item

        data_manager = getattr(self.data_processor, 'data_manager', None)
        if data_manager is None:
            return None

        try:
            refreshed = data_manager.load_custom_curves()
        except Exception as exc:
            print(f"Не удалось перечитать пользовательские кривые: {exc}")
            return None

        try:
            self.data_processor.other_data = list(refreshed)
        except Exception:
            self.data_processor.other_data = refreshed

        for item in getattr(self.data_processor, 'other_data', []) or []:
            if matches(item):
                return item

        return None

    def _persist_custom_curve_style(self, curve_id, style):
        custom_curve = self._get_cached_custom_curve(curve_id)

        if custom_curve is None:
            return False

        try:
            values = json.loads(custom_curve.values) if isinstance(custom_curve.values, str) else custom_curve.values
        except (TypeError, ValueError, json.JSONDecodeError):
            return False

        if not isinstance(values, dict):
            return False

        if values.get('type') == 'manual':
            style_dict = values.setdefault('style', {})
            for key in ('color', 'line_style', 'width', 'symbol', 'symbol_size', 'symbol_color', 'fill_color'):
                if key in style:
                    style_dict[key] = style[key]
        else:
            mapping = {
                'color': 'color',
                'width': 'line_width',
                'line_style': 'line_style',
                'symbol': 'symbol',
                'symbol_size': 'symbol_size',
                'symbol_color': 'symbol_color',
                'fill_color': 'fill_color',
            }
            for source_key, target_key in mapping.items():
                if source_key in style:
                    values[target_key] = style[source_key]

        serialized = json.dumps(values)

        try:
            updated = sp.new_upd_custom_curve((custom_curve.id, custom_curve.graph_project_id, serialized))
        except Exception as exc:
            print(f"Не удалось обновить стиль кривой {curve_id}: {exc}")
            return False
        else:
            if updated is not None and hasattr(updated, 'values'):
                custom_curve.values = updated.values
            else:
                custom_curve.values = serialized
            return True

    def _persist_test_curve_style(self, test_id, style):
        test_node = getattr(self.data_processor, 'test_nodes', {}).get(test_id)
        if test_node is None:
            return

        data = getattr(test_node, '_data', None)
        if data is None:
            return

        updates = {}

        color = style.get('color')
        if color:
            updates['curve_color'] = color

        width = style.get('width')
        if width is not None:
            updates['curve_width'] = int(width)

        line_style = style.get('line_style')
        if line_style is not None:
            updates['curve_line_style'] = int(GraphConstants.resolve_pen_style(line_style))

        symbol = style.get('symbol')
        if symbol is not None:
            updates['curve_point_symbol'] = symbol if symbol is not None else 'None'
        elif 'symbol' in style:
            updates['curve_point_symbol'] = 'None'

        symbol_size = style.get('symbol_size')
        if symbol_size is not None:
            updates['curve_point_size'] = int(symbol_size)

        symbol_color = style.get('symbol_color') or color
        if symbol_color is not None:
            updates['curve_symbol_color'] = symbol_color

        fill_color = style.get('fill_color') or symbol_color
        if fill_color is not None:
            updates['curve_symbol_fill_color'] = fill_color

        if not updates:
            return

        props_payload = []
        parent_id = getattr(data, 'id_up', None)
        if parent_id is None:
            parent_id = getattr(data, 'id_up_prod', None)

        for prop_name, prop_value in updates.items():
            props_payload.append((
                None,
                data.id,
                parent_id,
                7,
                prop_name,
                '' if prop_value is None else str(prop_value),
                None,
                None,
                None,
                0,
                None
            ))

        try:
            updated_props = sp.new_update_project_from_record_array(props_payload)
        except Exception as exc:
            print(f"Не удалось обновить стиль испытания {test_id}: {exc}")
            return

        if updated_props:
            if hasattr(test_node, 'update_class_props'):
                test_node.update_class_props(updated_props)

            for prop_name, prop_value in updates.items():
                value = prop_value
                if isinstance(value, str) and value.lower() in {'none', ''}:
                    if prop_name in {'curve_point_symbol', 'curve_symbol_color', 'curve_symbol_fill_color'}:
                        value = None
                setattr(test_node, prop_name, value)
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
