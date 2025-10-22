from __future__ import annotations

from typing import Dict, Optional

import pyqtgraph as pg
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

from dialogs.base import BaseDialog
from resources.ui.ui_py.ui_line_style import Ui_LineStyleDialog
from app.plugins.project.core.constants import GraphConstants
from app.plugins.project import utils_ as project_utils


class CurveStyleDialog(BaseDialog):
    """Диалог настройки стиля кривой"""

    _LINE_STYLE_TO_NAME = {
        Qt.NoPen: "none",
        Qt.SolidLine: "solid",
        Qt.DashLine: "dash",
        Qt.DotLine: "dot",
        Qt.DashDotLine: "dashdot",
        Qt.DashDotDotLine: "dashdotdot",
    }

    def __init__(self, style: Optional[Dict[str, object]] = None, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_LineStyleDialog()
        self.ui.setupUi(self)

        self._initial_style: Dict[str, object] = style.copy() if style else {}

        self._example_curve = pg.PlotDataItem([0, 1], [0, 1])
        self._configure_preview()
        self._populate_controls()
        self._apply_initial_style()
        self._connect_signals()
        self._update_preview()

    def _configure_preview(self) -> None:
        plot_item = self.ui.plotView.plotItem
        plot_item.getAxis('bottom').setStyle(showValues=False)
        plot_item.getAxis('left').setStyle(showValues=False)
        plot_item.setRange(xRange=[0, 1], yRange=[0, 1], padding=0.05)
        plot_item.showGrid(True, True, 0.3)
        plot_item.vb.setMouseEnabled(x=False, y=False)
        plot_item.addItem(self._example_curve)

    def _populate_controls(self) -> None:
        line_style_names = [name for _, name in project_utils.LINE_STYLES]
        self.ui.lineType.clear()
        self.ui.lineType.addItems(line_style_names)

        self._symbol_options = [(None, 'Без маркера')] + list(project_utils.SYMBOLS)
        symbol_names = [name for _, name in self._symbol_options]
        self.ui.pointType.clear()
        self.ui.pointType.addItems(symbol_names)

        self.ui.thickness.setRange(1, 10)
        self.ui.pointSizeSpinBox.setRange(1, 30)

    def _apply_initial_style(self) -> None:
        style = self._initial_style

        color = QColor(style.get('color', '#1f77b4'))
        if not color.isValid():
            color = QColor('#1f77b4')
        self.ui.colorButton.setColor(color)

        pen_style = GraphConstants.resolve_pen_style(style.get('line_style'))
        line_index = next(
            (i for i, (qt_style, _) in enumerate(project_utils.LINE_STYLES)
             if qt_style == pen_style),
            1  # Qt.SolidLine по умолчанию
        )
        self.ui.lineType.setCurrentIndex(line_index)

        width = int(style.get('width', 2))
        self.ui.thickness.setValue(width if width > 0 else 1)

        symbol_value = style.get('symbol')
        if symbol_value is None:
            symbol_index = 0
        else:
            symbol_index = next(
                (i for i, (value, _) in enumerate(self._symbol_options)
                 if value == symbol_value),
                0
            )
        self.ui.pointType.setCurrentIndex(symbol_index)

        size = int(style.get('symbol_size', 8))
        self.ui.pointSizeSpinBox.setValue(size if size > 0 else 1)

    def _connect_signals(self) -> None:
        self.ui.colorButton.sigColorChanged.connect(self._update_preview)
        self.ui.lineType.currentIndexChanged.connect(self._update_preview)
        self.ui.thickness.valueChanged.connect(self._update_preview)
        self.ui.pointType.currentIndexChanged.connect(self._update_preview)
        self.ui.pointSizeSpinBox.valueChanged.connect(self._update_preview)
        self.ui.okButton.clicked.connect(self.accept)

    def _get_current_controls(self):
        color = self.ui.colorButton.color()
        line_style, _ = project_utils.LINE_STYLES[self.ui.lineType.currentIndex()]
        width = self.ui.thickness.value()
        symbol_value, _ = self._symbol_options[self.ui.pointType.currentIndex()]
        symbol_size = self.ui.pointSizeSpinBox.value()
        return color, line_style, width, symbol_value, symbol_size

    def _update_preview(self) -> None:
        color, line_style, width, symbol_value, symbol_size = self._get_current_controls()
        self._example_curve.setPen(color=color, width=width, style=line_style)
        self._example_curve.setSymbol(symbol_value)
        self._example_curve.setSymbolSize(symbol_size)
        if symbol_value is None:
            self._example_curve.setSymbolPen(None)
            self._example_curve.setSymbolBrush(None)
        else:
            self._example_curve.setSymbolPen(color)
            self._example_curve.setSymbolBrush(color)

    def _convert_line_style_to_name(self, line_style: Qt.PenStyle) -> str:
        return self._LINE_STYLE_TO_NAME.get(line_style, 'solid')

    def get_style(self) -> Dict[str, object]:
        base_style = self._initial_style.copy()
        color, line_style, width, symbol_value, symbol_size = self._get_current_controls()

        base_style.update({
            'color': color.name(),
            'line_style': self._convert_line_style_to_name(line_style),
            'width': int(width),
            'symbol': symbol_value,
            'symbol_size': int(symbol_size),
        })
        return base_style

    def accept(self) -> None:
        self.res = self.get_style()
        super().accept()
