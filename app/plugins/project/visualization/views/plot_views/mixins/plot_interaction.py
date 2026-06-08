import PySide6
import pyqtgraph as pg
from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QGraphicsItem
from typing import Any, Callable

from pyqtgraph import PlotWidget

from app.basic_funcs import to_bool


class PlotInteractionMixin:
    """Миксин для обработки взаимодействия пользователя с графиком"""

    plotItem: Any
    scene: Any
    addItem: Callable
    mapSceneToView: Callable
    scene: Callable
    curve_items: list
    selected_points: dict
    item: Any

    def __init__(self):
        self.text_item = pg.TextItem()
        self.lastMousePos = None
        self.always_show_coordinates = True

        # Инициализация прокси для событий мыши
        self.proxy = self.init_proxy_for_mouse_move()
        self.proxy_click = self.init_proxy_for_mouse_click()

    def init_proxy_for_mouse_move(self):
        return pg.SignalProxy(
            self.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.onMouseMoved
        )

    def init_proxy_for_mouse_click(self):
        return pg.SignalProxy(
            self.scene().sigMouseClicked,
            rateLimit=60,
            slot=self.onMouseClicked
        )

    def apply_grid_settings(self):
        """Применяет настройки шага сетки к графику"""
        # Включаем отображение сетки
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)

        # Получаем настройки для осей X и Y
        x_config = self._get_grid_config('x')
        y_config = self._get_grid_config('y')

        # Ось X
        x_axis = self.plotItem.getAxis('bottom')
        if x_config['major']:
            # Ручной режим
            minor = x_config['minor'] or x_config['major'] / 5
            x_axis.setTickSpacing(major=x_config['major'], minor=minor)
        else:
            # Автоматический режим
            x_axis.enableAutoSIPrefix(True)
            x_axis.autoScale = True
            # Сбрасываем установленные ранее ручные значения
            x_axis.setTickSpacing(major=None, minor=None)
            x_axis.picture = None
            x_axis.update()

        # Ось Y
        y_axis = self.plotItem.getAxis('left')
        if y_config['major']:
            # Ручной режим
            minor = y_config['minor'] or y_config['major'] / 5
            y_axis.setTickSpacing(major=y_config['major'], minor=minor)
        else:
            # Автоматический режим
            y_axis.enableAutoSIPrefix(True)
            y_axis.autoScale = True
            # Сбрасываем установленные ранее ручные значения
            y_axis.setTickSpacing(major=None, minor=None)
            y_axis.picture = None
            y_axis.update()

        # Обновляем график
        self.plotItem.update()

    @staticmethod
    def _format_points_info_html(curve, points_data):
        """Форматирует HTML для отображения информации о группе точек одной кривой"""
        # Получаем цвет кривой
        color = None
        if 'symbolBrush' in curve.opts and curve.opts['symbolBrush'] is not None:
            color = curve.opts['symbolBrush'].color()
        elif 'pen' in curve.opts and curve.opts['pen'] is not None:
            color = curve.opts['pen'].color()

        if color is None:
            curve_color = "rgb(0, 0, 255)"
        else:
            curve_color = f"rgb({color.red()}, {color.green()}, {color.blue()})"

        html = f"""
        <div>
            <table style="background-color: white; margin: 2px; border-spacing: 0; border-collapse: collapse;">
                <tr>
                    <td style="background-color: {curve_color}; min-width: 1px; padding: 0;"></td>
                    <td style="background-color: {curve_color}; min-width: 1px; padding: 0;"></td>
                    <td style="background-color: {curve_color}; min-width: 1px; padding: 0;"></td>
                    <td style="padding: 8px;">
                        <div>
                            <span style="display: inline-block; width: 8px; height: 8px; background-color: {curve_color}; border-radius: 50%; margin-right: 5px;"></span>
                            <span style="color: black; font-weight: bold;">{curve.name()}</span>
                        </div>
        """

        # Добавляем информацию о точках
        for point_data in points_data:
            index, x, y = point_data
            html += f"""
                <div style="margin-left: 13px; color: black;">
                    • #{index + 1}: ({x:.4f}, {y:.4f})
                </div>
            """

        # Добавляем дополнительные данные, если они есть
        if hasattr(curve, 'get_point_info'):
            added_info = {}
            for index, _, _ in points_data:
                additional_info = curve.get_point_info(index)
                if additional_info:
                    for key, value in additional_info.items():
                        if key not in added_info:
                            added_info[key] = []
                        added_info[key].append(value)

            for key, values in added_info.items():
                if len(set(values)) == 1:  # Если все значения одинаковые
                    html += f"""
                        <div style="margin-left: 13px; color: black;">
                            <b>{key}:</b> {values[0]}
                        </div>
                    """
                else:
                    html += f"""
                        <div style="margin-left: 13px; color: black;">
                            <b>{key}:</b>
                    """
                    for i, value in enumerate(values):
                        html += f"""
                            <div style="margin-left: 13px;">
                                • точка #{i}: {value}
                            </div>
                        """
                    html += "</div>"

        html += """
                    </td>
                </tr>
            </table>
        </div>
        """
        return html

    def onMouseMoved(self, evt):
        """Обработчик движения мыши"""
        pos = evt[0]
        vb = self.plotItem.vb
        mouse_point = vb.mapSceneToView(pos)
        self.lastMousePos = pos  # Сохраняем позицию курсора

        # Проверяем, находится ли курсор в пределах видимой области
        view_bounds = vb.viewRect()
        is_in_bounds = (view_bounds.contains(mouse_point.x(), mouse_point.y()))

        point_info_found = False
        points_by_curve = {}

        # Собираем информацию о точках, сгруппированную по кривым
        for curve in self.curve_items:
            # Пропускаем скрытые кривые
            if not curve.isVisible():
                continue

            if hasattr(curve, 'scatter') and curve.scatter is not None:
                points = curve.scatter.points()
                hovered_points = curve.scatter._maskAt(mouse_point)

                unique_points = set()

                for i, (point, is_hovered) in enumerate(zip(points, hovered_points)):
                    if is_hovered and i not in unique_points:
                        point_info_found = True
                        unique_points.add(i)
                        x_data = curve.xData[i] if hasattr(curve, 'xData') else point.pos().x()
                        y_data = curve.yData[i] if hasattr(curve, 'yData') else point.pos().y()

                        if curve not in points_by_curve:
                            points_by_curve[curve] = []
                        points_by_curve[curve].append((i, x_data, y_data))

                    # Обновляем размер точки
                    if i in self.selected_points[curve]:
                        # Для выделенных точек всегда используем красный цвет и увеличенный размер
                        point.setBrush(pg.mkBrush('red'))
                        point.setSize(self._get_point_size(curve, 1.2, selected=True))
                    elif is_hovered:
                        # Для наведения используем оригинальный цвет
                        point.setSize(self._get_point_size(curve, 1.2))
                    else:
                        # Обычное состояние
                        point.setSize(self._get_point_size(curve, 1.0))

        # Формируем HTML для всех кривых
        if points_by_curve:
            all_curves_html = []
            for curve, points_data in points_by_curve.items():
                curve_html = self._format_points_info_html(curve, points_data)
                all_curves_html.append(curve_html)

            combined_html = "<div style='display: flex; flex-direction: column; gap: 5px;'>" + "".join(
                all_curves_html) + "</div>"
            self.text_item.setHtml(combined_html)
            self.text_item.setParentItem(self.plotItem)
            
            # Убедимся, что табличка не выходит за границы виджета
            self._position_text_item(pos)
            self.text_item.show()
        elif self.always_show_coordinates and not point_info_found and is_in_bounds:
            self.text_item.setHtml(
                f"<div style='text-align: center'><span style='color: black;'>{mouse_point.x():.2f}; {mouse_point.y():.2f}</span></div>")
            self.text_item.setParentItem(self.plotItem)
            
            # Убедимся, что табличка не выходит за границы виджета
            self._position_text_item(pos)
            self.text_item.show()
        else:
            self.text_item.hide()

    def onMouseClicked(self, evt):
        """Обрабатывает левый клик мыши по точкам на графике.

        Выделяет точку при клике по ней или снимает выделение при клике точно
        по уже выделенной точке. Выделенные точки отображаются красным цветом
        и увеличенным размером.
        """
        # Проверяем, что это левый клик мыши
        if evt[0].button() != Qt.LeftButton:
            return

        pos = evt[0].scenePos()
        mouse_point = self.plotItem.vb.mapSceneToView(pos)

        for curve in self.curve_items:
            if not self._is_curve_clickable(curve):
                continue

            self._try_handle_point_click(curve, pos, mouse_point)

    def _is_curve_clickable(self, curve):
        """Проверяет, можно ли кликнуть по точкам кривой"""
        return (curve.isVisible() and
                hasattr(curve, 'scatter') and
                curve.scatter is not None)

    def _try_handle_point_click(self, curve, scene_pos, view_pos):
        """Пытается обработать клик по точке на кривой.

        Args:
            curve: Кривая для проверки
            scene_pos: Позиция клика в координатах сцены
            view_pos: Позиция клика в координатах представления

        Returns:
            bool: True если клик был обработан
        """
        points = curve.scatter.points()
        clicked_points = curve.scatter._maskAt(view_pos)

        points_clicked = False
        for i, (point, is_clicked) in enumerate(zip(points, clicked_points)):
            if not is_clicked:
                continue

            if self._should_toggle_point_selection(curve, point, i, scene_pos):
                self._toggle_point_selection(curve, point, i)
                points_clicked = True

        if points_clicked:
            self.update()
            return True

        return False

    def _should_toggle_point_selection(self, curve, point, index, scene_pos):
        """Определяет, нужно ли переключить состояние выделения точки."""
        if index not in self.selected_points[curve]:
            return True

        # Для выделенной точки проверяем точность клика
        point_pos = point.pos()
        view_pos = self.plotItem.vb.mapViewToScene(QPointF(point_pos.x(), point_pos.y()))

        dx = scene_pos.x() - view_pos.x()
        dy = scene_pos.y() - view_pos.y()
        distance = (dx * dx + dy * dy) ** 0.5

        return distance <= point.size() / 2

    def _toggle_point_selection(self, curve, point, index):
        """Переключает состояние выделения точки."""
        if index in self.selected_points[curve]:
            self.selected_points[curve].remove(index)
            original_color = curve.opts['symbolBrush'].color()
            point.setBrush(pg.mkBrush(original_color))
            point.setSize(self._get_point_size(curve, 1.0))
        else:
            self.selected_points[curve].add(index)
            point.setBrush(pg.mkBrush('red'))
            point.setSize(self._get_point_size(curve, 1.2, selected=True))

    def _get_point_size(self, curve, scale_factor, selected=False):
        base_size = curve.point_size
        selected_addition = curve.selected_curve_point_size

        if selected:
            return (float(selected_addition) + 1) * int(base_size) * scale_factor
        return int(base_size) * scale_factor

    def _get_grid_config(self, axis: str) -> dict:
        """Получает конфигурацию сетки для оси"""
        grid_settings = self.get_grid_settings()
        axis_settings = grid_settings.get(axis, {'auto': True})
        if axis_settings.get('auto', True):
            return {'major': None, 'minor': None}

        return {
            'major': axis_settings.get('major'),
            'minor': axis_settings.get('minor')
        }

    def addItem(self, item: Any) -> None:
        # Implementation of addItem method
        pass

    def mapSceneToView(self, point: QPointF) -> QPointF:
        # Implementation of mapSceneToView method
        pass

    def scene(self) -> Any:
        # Implementation of scene method
        pass

    def _position_text_item(self, pos):
        """Позиционирует табличку с информацией так, чтобы она не выходила за границы виджета"""
        # Получаем размер виджета
        view_rect = self.plotItem.vb.viewRect()
        view_width = view_rect.width()
        view_height = view_rect.height()
        
        # Получаем размер таблички
        text_rect = self.text_item.boundingRect()
        text_width = text_rect.width()
        text_height = text_rect.height()
        
        # Получаем текущие координаты сцены в координатах представления
        scene_point = pos
        view_point = self.plotItem.vb.mapSceneToView(scene_point)
        
        # Получаем границы видимой области
        min_x = view_rect.left()
        max_x = view_rect.right()
        min_y = view_rect.top()
        max_y = view_rect.bottom()
        
        # Стандартное смещение
        offset_x = 10
        offset_y = -10
        
        # Конвертируем размеры из виджета в координаты представления
        # Мы сделаем приблизительную оценку
        scene_width = self.size().width()
        scene_height = self.size().height()
        
        # Приблизительное соотношение размеров представления и сцены
        width_ratio = view_width / scene_width
        height_ratio = view_height / scene_height
        
        # Приблизительные размеры текста в координатах представления
        text_view_width = text_width * width_ratio
        text_view_height = text_height * height_ratio
        
        # Проверяем выход за правую границу
        if view_point.x() + offset_x + text_view_width > max_x:
            # Если выходит, размещаем слева от курсора
            offset_x = -offset_x - text_view_width
        
        # Проверяем выход за нижнюю границу
        if view_point.y() + offset_y + text_view_height > max_y:
            # Если выходит, размещаем выше текста
            offset_y = -offset_y - text_view_height
        
        # Проверяем выход за верхнюю границу
        if view_point.y() + offset_y < min_y:
            # Если выходит, размещаем ниже курсора
            offset_y = abs(offset_y)
        
        # Проверяем выход за левую границу
        if view_point.x() + offset_x < min_x:
            # Если выходит, размещаем справа от курсора
            offset_x = abs(offset_x)
        
        # Устанавливаем позицию таблички в координатах сцены
        self.text_item.setPos(scene_point.x() + offset_x, scene_point.y() + offset_y)
