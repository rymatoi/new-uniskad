from typing import Optional, Any, Callable
import numpy as np

from app import app_logger
from app.plugins.project.core.constants import GraphConstants
from app.plugins.project.services.approximation import ApproximationService
from app.plugins.project.services.data_processors.plot_dp import PlotProcessor
from app.plugins.project.services.interpolation import Interpolation
from app.plugins.project.services.extrapolation import ExtrapolationService
from app.plugins.project.data.datamanagers.graph_datamanager import GraphDataManager

logger = app_logger.get_logger(__name__)


class PlotApproximationMixin:
    """Миксин для добавления аппроксимированных кривых на график"""

    add_curve: Callable
    data_manager: GraphDataManager
    data_processor: PlotProcessor

    def add_approximated_curve(
            self,
            source_curve: Any,
            degree: int = 2,
            name: Optional[str] = None,
            color: Optional[str] = None,
            line_width: Optional[int] = None,
            save_to_db: bool = True
    ) -> None:
        """Добавляет аппроксимированную кривую на график на основе исходной кривой
        
        Args:
            source_curve: Исходная кривая для аппроксимации
            degree: Степень полинома
            name: Название новой кривой
            color: Цвет линии (в формате HEX)
            line_width: Толщина линии
            save_to_db: Сохранять ли кривую в БД
        """
        try:
            x_data = source_curve.xData
            y_data = source_curve.yData

            # Используем сервис для аппроксимации
            x_smooth, y_smooth = ApproximationService.polynomial_fit(x_data, y_data, degree)

            # Создаем новый стиль на основе стиля исходной кривой
            curve_style = GraphConstants.APPROXIMATION_STYLE.copy()
            
            # Применяем пользовательские настройки стиля, если они указаны
            if color:
                curve_style['color'] = color
            else:
                curve_style['color'] = source_curve.style['fill_color'] if 'fill_color' in source_curve.style else '#1f77b4'
                
            if line_width is not None:
                curve_style['width'] = line_width

            # Добавляем кривую через существующий метод с новым стилем
            curve_name = name or f"Approximation (deg={degree})"
            new_curve = self.add_curve(x_smooth, y_smooth, name=curve_name, **curve_style)

            # Сохраняем в БД, если требуется
            if save_to_db:
                custom_curve_id = self.data_processor.save_approximation(
                    test_id=self.data_processor.get_test_id_for_curve(source_curve),
                    name=curve_name,
                    degree=degree,
                    color=color,
                    line_width=line_width
                )
                # Устанавливаем ID для новой кривой
                if new_curve and custom_curve_id:
                    new_curve.custom_curve_id = custom_curve_id

        except Exception as e:
            logger.error(f"Ошибка при построении аппроксимации: {str(e)}")
            raise

    def add_interpolated_curve(
            self,
            source_curve: Any,
            kind: str = 'quadratic',
            num_points: int = 1000,
            name: Optional[str] = None,
            color: Optional[str] = None,
            line_width: Optional[int] = None,
            save_to_db: bool = True
    ) -> None:
        """Добавляет интерполированную кривую на график на основе исходной кривой
        
        Args:
            source_curve: Исходная кривая для интерполяции
            kind: Тип интерполяции
            num_points: Количество точек
            name: Название новой кривой
            color: Цвет линии (в формате HEX)
            line_width: Толщина линии
            save_to_db: Сохранять ли кривую в БД
        """
        try:
            x_data = source_curve.xData
            y_data = source_curve.yData

            # Используем сервис для интерполяции
            x_smooth, y_smooth = Interpolation.quadratic_interpolation(x_data, y_data, num_points, kind=kind)

            # Создаем новый стиль
            curve_style = GraphConstants.INTERPOLATION_STYLE.copy()
            
            # Применяем пользовательские настройки стиля, если они указаны
            if color:
                curve_style['color'] = color
            else:
                curve_style['color'] = source_curve.style['fill_color'] if 'fill_color' in source_curve.style else '#1f77b4'
                
            if line_width is not None:
                curve_style['width'] = line_width

            # Добавляем кривую
            curve_name = name or f"Interpolation ({kind})"
            new_curve = self.add_curve(x_smooth, y_smooth, name=curve_name, **curve_style)

            # Сохраняем в БД, если требуется
            if save_to_db:
                custom_curve_id = self.data_processor.save_interpolation(
                    test_id=self.data_processor.get_test_id_for_curve(source_curve),
                    name=curve_name,
                    interp_type=kind,
                    color=color,
                    line_width=line_width
                )
                # Устанавливаем ID для новой кривой
                if new_curve and custom_curve_id:
                    new_curve.custom_curve_id = custom_curve_id

        except Exception as e:
            logger.error(f"Ошибка при построении интерполяции: {str(e)}")
            raise

    def add_extrapolated_curve(
            self,
            source_curve: Any,
            left_points: int = 20,
            right_points: int = 20,
            degree: int = 2,
            name: Optional[str] = None,
            *,
            left_limit: Optional[float] = None,
            right_limit: Optional[float] = None,
    ) -> None:
        """Добавляет экстраполированную кривую на график на основе исходной кривой"""
        try:
            x_data = source_curve.xData
            y_data = source_curve.yData

            # Используем сервис для экстраполяции
            x_extrap, y_extrap = ExtrapolationService.polynomial_extrapolation(
                x_data,
                y_data,
                left_points,
                right_points,
                degree,
                left_limit=left_limit,
                right_limit=right_limit,
            )

            # Создаем новый стиль
            curve_style = GraphConstants.EXTRAPOLATION_STYLE.copy()
            source_style = getattr(source_curve, 'style', {}) or {}
            base_color = source_style.get('color', curve_style['color'])
            fill_color = source_style.get('fill_color')
            curve_style['color'] = fill_color or base_color

            # Добавляем кривую
            curve_name = name or f"Extrapolation (deg={degree})"
            self.add_curve(x_extrap, y_extrap, name=curve_name, **curve_style)

        except Exception as e:
            logger.error(f"Ошибка при построении экстраполяции: {str(e)}")
            raise
