from typing import Any, Optional, TypeVar, List, Dict, Set, Callable
import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import Qt, QPointF
from app import app_logger

logger = app_logger.get_logger(__name__)

PlotWidgetType = TypeVar('PlotWidgetType', bound='pg.PlotWidget')


class RulerInstance:
    """Класс для представления одной линейки на графике"""
    
    def __init__(self, parent, position=0):
        self.enabled = False
        self.pos = position
        self.line = pg.InfiniteLine(
            angle=90,
            movable=True,
            pen=pg.mkPen((255, 0, 0), width=2, style=Qt.SolidLine),
        )

        self.label = pg.InfLineLabel(
            self.line,
            text="Δy",
            movable=True,
            position=0.1,
            color=(0, 0, 0),
        )

        self.delta_line = pg.PlotDataItem(parent=parent)
        self.curve1 = None
        self.curve2 = None
        self.last_pos = None
        
        self.line.setVisible(False)
        self.delta_line.setVisible(False)
        
        # ID линейки для идентификации
        self.id = None


class PlotRulerMixin:
    """Миксин для работы с линейками для измерения расстояния между кривыми"""

    plotItem: Any
    addItem: Callable
    removeItem: Callable
    
    def __init__(self):
        """Инициализация миксина"""
        self.init_rulers()
    
    def init_rulers(self):
        """Инициализация системы линеек"""
        # Словарь всех линеек по их id
        self.rulers = {}
        # Счетчик для генерации уникальных id
        self.ruler_id_counter = 0
        # Текущая активная линейка
        self.active_ruler_id = None
        
    def create_ruler(self):
        """
        Создает новую линейку
        
        Returns:
            int: ID созданной линейки
        """
        ruler = RulerInstance(self)
        
        # Присваиваем уникальный ID
        ruler_id = self.ruler_id_counter
        self.ruler_id_counter += 1
        ruler.id = ruler_id
        
        # Подключаем обработчик изменения позиции
        ruler.line.sigPositionChanged.connect(lambda: self.update_ruler(ruler_id))
        
        # Добавляем в словарь
        self.rulers[ruler_id] = ruler
        
        # Делаем активной
        self.active_ruler_id = ruler_id
        
        print(f"Создана новая линейка с ID {ruler_id}")
        return ruler_id
    
    def add_ruler(self, ruler_id=None):
        """
        Добавление линейки на график
        
        Args:
            ruler_id: ID линейки для добавления. Если None, используется активная линейка
        """
        # Если ID не указан, используем активную линейку
        if ruler_id is None:
            # Если нет активной линейки, создаем новую
            if self.active_ruler_id is None:
                ruler_id = self.create_ruler()
            else:
                ruler_id = self.active_ruler_id
        
        # Проверяем существование линейки
        if ruler_id not in self.rulers:
            print(f"Линейка с ID {ruler_id} не найдена")
            return
            
        ruler = self.rulers[ruler_id]
        
        # Проверяем, что линейка ещё не добавлена
        if not ruler.enabled:
            # Установка высокого z-индекса для отображения поверх других элементов
            ruler.line.setZValue(100)
            ruler.delta_line.setZValue(100)
            
            # Явно устанавливаем цвет и толщину для лучшей видимости
            ruler.line.setPen(pg.mkPen((255, 0, 0), width=2, style=Qt.SolidLine))
            ruler.delta_line.setPen(pg.mkPen((255, 0, 0), width=2, style=Qt.SolidLine))
            
            # Добавляем элементы на график
            self.addItem(ruler.line, ignoreBounds=True)
            self.addItem(ruler.delta_line)
            
            # Устанавливаем флаги и видимость
            ruler.enabled = True
            ruler.line.setVisible(True)
            ruler.delta_line.setVisible(True)
            
            print(f"Линейка {ruler_id} добавлена на график, видимость: {ruler.line.isVisible()}, z-индекс: {ruler.line.zValue()}")
            # Принудительно обновляем отображение линейки
            self.update_ruler(ruler_id)
            
            # Выводим линейку на передний план
            self.bring_to_front(ruler_id)
        else:
            print(f"Линейка {ruler_id} уже добавлена на график")

    def remove_ruler(self, ruler_id=None):
        """
        Удаление линейки с графика
        
        Args:
            ruler_id: ID линейки для удаления. Если None, используется активная линейка
        """
        # Если ID не указан, используем активную линейку
        if ruler_id is None:
            if self.active_ruler_id is None:
                print("Нет активной линейки для удаления")
                return
            ruler_id = self.active_ruler_id
            
        # Проверяем существование линейки
        if ruler_id not in self.rulers:
            print(f"Линейка с ID {ruler_id} не найдена")
            return
            
        ruler = self.rulers[ruler_id]
        
        if ruler.enabled:
            self.removeItem(ruler.line)
            self.removeItem(ruler.delta_line)
            ruler.enabled = False
            ruler.line.setVisible(False)
            ruler.delta_line.setVisible(False)
            ruler.label.setVisible(False)
            ruler.curve1 = None
            ruler.curve2 = None
            ruler.last_pos = None
            ruler.delta_line.setData([], [])
            if self.active_ruler_id == ruler_id:
                self.active_ruler_id = None
            logger.info("Линейка %s удалена с графика", ruler_id)

    def remove_all_rulers(self):
        """Remove every ruler and all of its scene items/references."""
        for ruler_id in list(self.rulers):
            self.remove_ruler(ruler_id)
        self.active_ruler_id = None
        logger.info("Все линейки удалены с графика")
    
    def _y_pos(self, x_pos: float, curve: pg.PlotDataItem) -> Optional[float]:
        """Найти значение функции в точке ``x_pos`` для кривой ``curve``."""
        if curve and hasattr(curve, 'xData') and hasattr(curve, 'yData'):
            if len(curve.xData) > 0 and len(curve.yData) > 0:
                # Проверяем, находится ли x_pos в диапазоне данных кривой
                if curve.xData[0] <= x_pos <= curve.xData[-1]:
                    y_pos = np.interp(x_pos, curve.xData, curve.yData)
                    print(f"Интерполированное значение для кривой {curve.name() if hasattr(curve, 'name') else 'без имени'}: {y_pos}")
                    return y_pos
                else:
                    print(f"x_pos={x_pos} вне диапазона кривой {curve.xData[0]} - {curve.xData[-1]}")
            else:
                print(f"Кривая {curve.name() if hasattr(curve, 'name') else 'без имени'} не имеет данных")
        return None
    
    def update_ruler(self, ruler_id=None):
        """
        Перемещение/обновление таблички с данными линейки
        
        Args:
            ruler_id: ID линейки для обновления. Если None, используется активная линейка
        """
        # Если ID не указан, используем активную линейку
        if ruler_id is None:
            if self.active_ruler_id is None:
                print("Нет активной линейки для обновления")
                return
            ruler_id = self.active_ruler_id
            
        # Проверяем существование линейки
        if ruler_id not in self.rulers:
            print(f"Линейка с ID {ruler_id} не найдена")
            return
            
        ruler = self.rulers[ruler_id]
        
        if not ruler.enabled:
            if ruler.curve1 is None and ruler.curve2 is None:
                print(f"Линейка {ruler_id} отключена и не привязана к кривым, обновление не требуется")
                return
            print(f"Линейка {ruler_id} не активна, включаем её")
            self.add_ruler(ruler_id)
            return
            
        x_pos = ruler.line.pos().x()
        y1_pos = self._y_pos(x_pos, ruler.curve1)
        y2_pos = self._y_pos(x_pos, ruler.curve2)

        print(f"update_ruler {ruler_id}: x_pos={x_pos}, y1_pos={y1_pos}, y2_pos={y2_pos}")
        print(f"Кривые: curve1={ruler.curve1.name() if ruler.curve1 and hasattr(ruler.curve1, 'name') else None}, curve2={ruler.curve2.name() if ruler.curve2 and hasattr(ruler.curve2, 'name') else None}")

        if y1_pos is None and y2_pos is None:
            y1 = y2 = 0
            print("Обе кривые дали None значения в текущей позиции")
        else:
            # Если одно из значений None, используем другое для обоих
            y1 = y1_pos if y1_pos is not None else (y2_pos if y2_pos is not None else 0)
            y2 = y2_pos if y2_pos is not None else (y1_pos if y1_pos is not None else 0)
            
        ruler.last_pos = (x_pos, y1)

        # Рассчитываем разницу значений
        dy = abs(y2 - y1) if y1 is not None and y2 is not None else 0

        # Получаем имена кривых
        curve1_name = '-'
        curve2_name = '-'
        
        if ruler.curve1:
            curve1_name = ruler.curve1.name() if hasattr(ruler.curve1, 'name') else '-'
            
        if ruler.curve2:
            curve2_name = ruler.curve2.name() if hasattr(ruler.curve2, 'name') else '-'

        # Формируем текст метки
        y_ratio = 'inf'
        if y2 and y1:
            try:
                y_ratio = float(y1) / float(y2)
            except (ZeroDivisionError, TypeError):
                y_ratio = 'inf'

        y_avg = 'N/A'
        if y1 is not None and y2 is not None:
            try:
                y_avg = float((float(y1) + float(y2)) / 2)
            except (TypeError, ValueError):
                y_avg = 'N/A'

        # Обновляем текст метки
        ruler.label.setText(
            f"#{ruler_id}: Δy={dy}\n"
            f"y1 = {curve1_name}\n"
            f"y2 = {curve2_name}\n"
            f"y1/y2={y_ratio}\n"
            f"y ср.={y_avg}")
            
        # Проверяем видимость линейки
        if not ruler.line.isVisible():
            print(f"Линейка {ruler_id} невидима, делаем видимой")
            ruler.line.setVisible(True)

        # Обновляем линию с дельтой
        ruler.delta_line.setData([x_pos, x_pos], [y1, y2], symbolSize=10)
        ruler.delta_line.setPen(pg.mkPen(color=(255, 0, 0), width=2, style=Qt.SolidLine))
        
        # Явно устанавливаем видимость
        ruler.delta_line.setVisible(True)
        
        # Гарантируем, что линейка находится поверх других элементов
        ruler.line.setZValue(100)
        ruler.delta_line.setZValue(100)
        
        print(f"Линия дельты {ruler_id} обновлена: x={x_pos}, y1={y1}, y2={y2}, видима={ruler.delta_line.isVisible()}")

    def save_rulers_state(self):
        """
        Сохраняет текущее состояние всех линеек для последующего восстановления
        
        Returns:
            dict: Словарь с состоянием линеек
        """
        state = {
            'active_ruler_id': self.active_ruler_id,
            'rulers': {}
        }
        
        for ruler_id, ruler in self.rulers.items():
            ruler_state = {
                'enabled': ruler.enabled,
                'pos': ruler.line.pos().x() if ruler.line else None,
                'curve1_name': ruler.curve1.name() if ruler.curve1 and hasattr(ruler.curve1, 'name') else None,
                'curve2_name': ruler.curve2.name() if ruler.curve2 and hasattr(ruler.curve2, 'name') else None
            }
            state['rulers'][ruler_id] = ruler_state
            
        print(f"Сохранено состояние линеек: {len(self.rulers)} линеек, активная: {self.active_ruler_id}")
        return state
        
    def restore_rulers_state(self, state):
        """
        Восстанавливает состояние линеек из сохраненного
        
        Args:
            state (dict): Словарь с состоянием линеек
        """
        if not state or 'rulers' not in state:
            print("Нет данных для восстановления линеек")
            return
            
        print(f"Восстановление состояния линеек: {len(state['rulers'])} линеек")
        
        # Сначала удаляем все текущие линейки
        for ruler_id in list(self.rulers.keys()):
            self.remove_ruler(ruler_id)
        
        # Создаем новые линейки из сохраненного состояния
        for ruler_id_str, ruler_state in state['rulers'].items():
            ruler_id = int(ruler_id_str)
            
            # Находим кривые по именам
            curve1 = None
            curve2 = None
            
            for curve in self.curve_items:
                if hasattr(curve, 'name'):
                    curve_name = curve.name()
                    if curve_name == ruler_state.get('curve1_name'):
                        curve1 = curve
                        print(f"Найдена первая кривая для линейки {ruler_id}: {curve_name}")
                    elif curve_name == ruler_state.get('curve2_name'):
                        curve2 = curve
                        print(f"Найдена вторая кривая для линейки {ruler_id}: {curve_name}")
            
            # Если нашли хоть одну кривую, восстанавливаем линейку
            if curve1 or curve2:
                # Создаем линейку с нужным ID
                while self.ruler_id_counter <= ruler_id:
                    self.create_ruler()
                
                ruler = self.rulers[ruler_id]
                ruler.curve1 = curve1
                ruler.curve2 = curve2
                
                # Устанавливаем позицию
                if ruler_state.get('pos') is not None:
                    ruler.line.setPos(ruler_state.get('pos'))
                
                # Добавляем линейку на график, если она была активна
                if ruler_state.get('enabled', False):
                    self.add_ruler(ruler_id)
                
                print(f"Линейка {ruler_id} восстановлена")
        
        # Восстанавливаем активную линейку
        if 'active_ruler_id' in state and state['active_ruler_id'] in self.rulers:
            self.active_ruler_id = state['active_ruler_id']
            print(f"Восстановлена активная линейка: {self.active_ruler_id}")
    
    def set_active_ruler(self, ruler_id):
        """
        Устанавливает активную линейку
        
        Args:
            ruler_id: ID линейки для активации
        """
        if ruler_id in self.rulers:
            self.active_ruler_id = ruler_id
            print(f"Линейка {ruler_id} установлена как активная")
            return True
        else:
            print(f"Линейка с ID {ruler_id} не найдена")
            return False

    def set_ruler_mark(self, pos, curve=None, ruler_id=None):
        """
        Прикрепление линейки к кривым
        
        Args:
            pos: Позиция линейки (X-координата)
            curve: Кривая, к которой прикрепляется линейка
            ruler_id: ID линейки для работы. Если None, используется активная линейка
                     или создается новая
        """
        if not curve:
            return
            
        # Если ID не указан, используем активную линейку или создаем новую
        if ruler_id is None:
            if self.active_ruler_id is None or self.active_ruler_id not in self.rulers:
                ruler_id = self.create_ruler()
            else:
                ruler_id = self.active_ruler_id
                
        # Проверяем существование линейки
        if ruler_id not in self.rulers:
            print(f"Линейка с ID {ruler_id} не найдена")
            return
            
        ruler = self.rulers[ruler_id]
            
        if not ruler.curve1:
            # Первая метка - устанавливаем на первую кривую
            print(f"Установка первой метки на кривую {curve.name() if hasattr(curve, 'name') else 'без имени'} для линейки {ruler_id}")
            ruler.curve1 = curve
            ruler.line.setPos(pos)
            if not ruler.enabled:
                self.add_ruler(ruler_id)
        elif not ruler.curve2 and curve != ruler.curve1:
            # Вторая метка - устанавливаем на вторую кривую, если она отличается от первой
            print(f"Установка второй метки на кривую {curve.name() if hasattr(curve, 'name') else 'без имени'} для линейки {ruler_id}")
            ruler.curve2 = curve
            ruler.line.setPos(pos)
        elif curve == ruler.curve1:
            # Клик по кривой с первой меткой - снимаем метку и сдвигаем вторую метку на первую позицию
            print(f"Снятие метки с первой кривой {curve.name() if hasattr(curve, 'name') else 'без имени'} для линейки {ruler_id}")
            if ruler.curve2:
                ruler.curve1 = ruler.curve2
                ruler.curve2 = None
            else:
                ruler.curve1 = None
                self.remove_ruler(ruler_id)
        elif curve == ruler.curve2:
            # Клик по кривой со второй меткой - снимаем метку
            print(f"Снятие метки со второй кривой {curve.name() if hasattr(curve, 'name') else 'без имени'} для линейки {ruler_id}")
            ruler.curve2 = None
        else:
            # Клик по третьей кривой - заменяем вторую метку
            print(f"Замена второй метки на кривую {curve.name() if hasattr(curve, 'name') else 'без имени'} для линейки {ruler_id}")
            ruler.curve2 = curve
            ruler.line.setPos(pos)
            
        # Обновляем отображение линейки
        self.update_ruler(ruler_id)

        # Устанавливаем линейку как активную только если она привязана к кривым
        if ruler.curve1 or ruler.curve2:
            self.active_ruler_id = ruler_id
        elif self.active_ruler_id == ruler_id:
            self.active_ruler_id = None

    def bring_to_front(self, ruler_id=None):
        """
        Принудительно выводит линейку на передний план
        
        Args:
            ruler_id: ID линейки для вывода на передний план. Если None, используется активная линейка
        """
        # Если ID не указан, используем активную линейку
        if ruler_id is None:
            if self.active_ruler_id is None:
                print("Нет активной линейки для вывода на передний план")
                return
            ruler_id = self.active_ruler_id
            
        # Проверяем существование линейки
        if ruler_id not in self.rulers:
            print(f"Линейка с ID {ruler_id} не найдена")
            return
            
        ruler = self.rulers[ruler_id]
        
        if not ruler.enabled:
            print(f"Линейка {ruler_id} не активна, не можем вывести на передний план")
            return
            
        # Удаляем и добавляем заново элементы линейки
        try:
            self.removeItem(ruler.line)
            self.removeItem(ruler.delta_line)
        except Exception as e:
            print(f"Ошибка при удалении линейки {ruler_id}: {e}")
            
        # Установка стиля
        ruler.line.setPen(pg.mkPen((255, 0, 0), width=2, style=Qt.SolidLine))
        ruler.delta_line.setPen(pg.mkPen((255, 0, 0), width=2, style=Qt.SolidLine))
        
        # Установка высокого z-индекса
        ruler.line.setZValue(1000)
        ruler.delta_line.setZValue(1000)
        
        # Добавляем элементы обратно
        self.addItem(ruler.line, ignoreBounds=True)
        self.addItem(ruler.delta_line)
        
        # Устанавливаем видимость
        ruler.line.setVisible(True)
        ruler.delta_line.setVisible(True)
        
        print(f"Линейка {ruler_id} выведена на передний план: видимость={ruler.line.isVisible()}, z-индекс={ruler.line.zValue()}")
        
        # Обновляем отображение
        self.update_ruler(ruler_id)
        
    # Совместимость со старым интерфейсом
    def init_ruler(self):
        """Для обратной совместимости"""
        self.init_rulers()
        
    def save_ruler_state(self):
        """Для обратной совместимости"""
        return self.save_rulers_state()
        
    def restore_ruler_state(self, state):
        """Для обратной совместимости"""
        # Если это старое состояние с одной линейкой
        if isinstance(state, dict) and 'enabled' in state:
            # Преобразуем в новый формат
            new_state = {
                'active_ruler_id': 0,
                'rulers': {
                    '0': state
                }
            }
            self.restore_rulers_state(new_state)
        else:
            self.restore_rulers_state(state)
