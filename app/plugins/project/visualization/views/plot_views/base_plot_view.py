from typing import Optional
from app import app_logger
from .fps_plot_view import FPSPlotWidget
from .mixins.plot_approximation import PlotApproximationMixin
from .mixins.plot_context_menu import PlotContextMenuMixin
from .mixins.plot_data import PlotDataMixin
from .mixins.plot_interaction import PlotInteractionMixin
from .mixins.plot_display import PlotDisplayMixin
from .mixins.plot_ruler import PlotRulerMixin

logger = app_logger.get_logger(__name__)


class BasePlotView(FPSPlotWidget, PlotDataMixin, PlotInteractionMixin, PlotDisplayMixin, PlotContextMenuMixin,
                   PlotApproximationMixin, PlotRulerMixin):
    """Базовый класс для отображения графиков

    Объединяет функциональность для работы с данными, интерактивности и отображения графиков.
    Наследует возможности отображения FPS и дополняет их специфичной
    функциональностью через миксины.

    Args:
        item: Элемент данных для отображения
        main_window: Главное окно приложения
        parent: Родительский виджет (опционально)

    Attributes:
        Наследует атрибуты от FPSPlotWidget и всех подключенных миксинов
    """

    def __init__(self, item: any, main_window: any, parent: Optional[any] = None) -> None:
        # Инициализация родительских классов
        FPSPlotWidget.__init__(self, parent=parent)
        PlotRulerMixin.__init__(self)
        PlotDataMixin.__init__(self, item, main_window)
        PlotInteractionMixin.__init__(self)
        PlotDisplayMixin.__init__(self)
        PlotApproximationMixin.__init__(self)
        PlotContextMenuMixin.__init__(self)
        
        # Дополнительная инициализация атрибутов линейки
        self.ruler_curve1 = None
        self.ruler_curve2 = None
