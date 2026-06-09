# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'line_style.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from pyqtgraph import ColorButton
from pyqtgraph import PlotWidget


class Ui_LineStyleDialog(object):
    def setupUi(self, LineStyleDialog):
        if not LineStyleDialog.objectName():
            LineStyleDialog.setObjectName(u"LineStyleDialog")
        LineStyleDialog.resize(447, 226)
        LineStyleDialog.setStyleSheet(u"")
        self.gridLayout = QGridLayout(LineStyleDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.form = QFormLayout()
        self.form.setObjectName(u"form")
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.colorLabel = QLabel(LineStyleDialog)
        self.colorLabel.setObjectName(u"colorLabel")

        self.form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.colorLabel)

        self.colorButton = ColorButton(LineStyleDialog)
        self.colorButton.setObjectName(u"colorButton")
        self.colorButton.setMaximumSize(QSize(30, 30))
        self.colorButton.setStyleSheet(u"background-color: transparent;")
        self.colorButton.setAutoDefault(False)

        self.form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.colorButton)

        self.lineTypeLabel = QLabel(LineStyleDialog)
        self.lineTypeLabel.setObjectName(u"lineTypeLabel")

        self.form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lineTypeLabel)

        self.lineType = QComboBox(LineStyleDialog)
        self.lineType.setObjectName(u"lineType")
        self.lineType.setMinimumSize(QSize(200, 0))

        self.form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineType)

        self.thicknessLabel = QLabel(LineStyleDialog)
        self.thicknessLabel.setObjectName(u"thicknessLabel")

        self.form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.thicknessLabel)

        self.thickness = QSpinBox(LineStyleDialog)
        self.thickness.setObjectName(u"thickness")
        self.thickness.setValue(1)

        self.form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.thickness)

        self.pointTypeLabel = QLabel(LineStyleDialog)
        self.pointTypeLabel.setObjectName(u"pointTypeLabel")

        self.form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.pointTypeLabel)

        self.pointType = QComboBox(LineStyleDialog)
        self.pointType.setObjectName(u"pointType")

        self.form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.pointType)

        self.pointSizeLabel = QLabel(LineStyleDialog)
        self.pointSizeLabel.setObjectName(u"pointSizeLabel")

        self.form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.pointSizeLabel)

        self.pointSizeSpinBox = QSpinBox(LineStyleDialog)
        self.pointSizeSpinBox.setObjectName(u"pointSizeSpinBox")
        self.pointSizeSpinBox.setValue(10)

        self.form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.pointSizeSpinBox)

        self.horizontalLayout_3.addLayout(self.form)

        self.plotView = PlotWidget(LineStyleDialog)
        self.plotView.setObjectName(u"plotView")
        self.plotView.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_3.addWidget(self.plotView)

        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.okButton = QPushButton(LineStyleDialog)
        self.okButton.setObjectName(u"okButton")
        self.okButton.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_4.addWidget(self.okButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)

        self.retranslateUi(LineStyleDialog)

        self.okButton.setDefault(True)

        QMetaObject.connectSlotsByName(LineStyleDialog)

    # setupUi

    def retranslateUi(self, LineStyleDialog):
        LineStyleDialog.setWindowTitle(QCoreApplication.translate("LineStyleDialog",
                                                                  u"\u0418\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0435 \u0433\u0440\u0430\u0444\u0438\u043a\u0430",
                                                                  None))
        self.colorLabel.setText(QCoreApplication.translate("LineStyleDialog", u"\u0426\u0432\u0435\u0442", None))
        self.lineTypeLabel.setText(
            QCoreApplication.translate("LineStyleDialog", u"\u0422\u0438\u043f \u043b\u0438\u043d\u0438\u0438", None))
        self.thicknessLabel.setText(
            QCoreApplication.translate("LineStyleDialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None))
        self.pointTypeLabel.setText(
            QCoreApplication.translate("LineStyleDialog", u"\u0412\u0438\u0434 \u0442\u043e\u0447\u043a\u0438", None))
        self.pointSizeLabel.setText(QCoreApplication.translate("LineStyleDialog",
                                                               u"\u0420\u0430\u0437\u043c\u0435\u0440 \u0442\u043e\u0447\u043a\u0438",
                                                               None))
        self.okButton.setText(
            QCoreApplication.translate("LineStyleDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c",
                                       None))
    # retranslateUi
