from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from db.schemas import Menu


class ActionTarget(Enum):
    """Цель действия меню"""
    CURVE = auto()
    POINT = auto()
    PLOT = auto()


@dataclass
class MenuAction:
    """Описание действия меню"""
    name: str
    translation: str
    target: ActionTarget
    is_checkable: bool = False
    icon: Optional[str] = None
    shortcut: Optional[str] = None
    order: int = 100  # Добавляем порядок по умолчанию


class PlotMenuActions:
    """Класс, определяющий все доступные действия для графика"""

    # Действия для кривых
    CURVE_COPY = MenuAction("copy_curve", "Копировать кривую", ActionTarget.CURVE, order=20)
    CURVE_EXPORT = MenuAction("export_curve", "Экспортировать данные", ActionTarget.CURVE, order=21)
    CURVE_RULER_MARK = MenuAction("ruler_mark", "Метка для линейки", ActionTarget.CURVE, order=22)
    CURVE_APPROXIMATION = MenuAction("approximate", "Аппроксимировать..", ActionTarget.CURVE, order=60)
    CURVE_INTERPOLATION = MenuAction("interpolate", "Интерполировать..", ActionTarget.CURVE, order=70)
    CURVE_EXTRAPOLATION = MenuAction("extrapolate", "Экстраполировать..", ActionTarget.CURVE, order=80)
    CURVE_STYLE = MenuAction("customize_curve", "Настройка стиля..", ActionTarget.CURVE, order=81)
    CURVE_HIDE = MenuAction("hide_curve", "Скрыть кривую", ActionTarget.CURVE, is_checkable=True, order=90)
    CURVE_DELETE = MenuAction("delete_curve", "Удалить кривую", ActionTarget.CURVE, order=100)

    # Действия для точек
    POINT_INFO = MenuAction("point_info", "Информация о точке", ActionTarget.POINT, order=10)
    POINT_MARK = MenuAction("mark_point", "Отметить точку", ActionTarget.POINT, is_checkable=True, order=20)
    POINT_COPY = MenuAction("copy_point", "Копировать точку", ActionTarget.POINT, order=30)
    POINT_DELETE = MenuAction("delete_point", "Удалить точку", ActionTarget.POINT, order=40)

    # Действия для графика
    PLOT_RESET_VIEW = MenuAction("reset_view", "Сбросить масштаб", ActionTarget.PLOT, order=10)
    PLOT_GRID = MenuAction("toggle_grid", "Показать сетку", ActionTarget.PLOT, is_checkable=True, order=20)
    PLOT_LEGEND = MenuAction("toggle_legend", "Показать легенду", ActionTarget.PLOT, is_checkable=True, order=30)
    PLOT_LEGEND_SETTINGS = MenuAction("legend_settings", "Настройка легенды...", ActionTarget.PLOT, order=35)
    PLOT_EXPORT = MenuAction("export_plot", "Экспортировать график", ActionTarget.PLOT, order=40)

    @classmethod
    def get_all_actions(cls) -> List[MenuAction]:
        """Возвращает все доступные действия, отсортированные по порядку"""
        actions = [getattr(cls, attr) for attr in dir(cls)
                   if isinstance(getattr(cls, attr), MenuAction)]
        return sorted(actions, key=lambda x: x.order)

    @classmethod
    def get_actions_by_target(cls, target: ActionTarget) -> List[MenuAction]:
        """Возвращает все действия для указанной цели, отсортированные по порядку"""
        actions = [action for action in cls.get_all_actions()
                   if action.target == target]
        return sorted(actions, key=lambda x: x.order)


def get_action_name(action: Menu) -> str:
    return action.name[1:]


def get_available_actions(menu_items: List[Menu]) -> List[MenuAction]:
    """
    Возвращает список доступных действий на основе списка из БД
    
    Args:
        menu_items: Список элементов меню из БД
    """
    all_actions = PlotMenuActions.get_all_actions()
    available_names = {get_action_name(item) for item in menu_items}

    # Действия, которые всегда доступны
    always_available = {
        PlotMenuActions.PLOT_RESET_VIEW.name,
        PlotMenuActions.PLOT_GRID.name,
        PlotMenuActions.PLOT_LEGEND.name,
        PlotMenuActions.PLOT_LEGEND_SETTINGS.name,
        PlotMenuActions.POINT_INFO.name,
        PlotMenuActions.CURVE_STYLE.name,
        PlotMenuActions.CURVE_HIDE.name,
        PlotMenuActions.CURVE_DELETE.name,
    }

    return [action for action in all_actions
            if action.name in available_names or action.name in always_available]
