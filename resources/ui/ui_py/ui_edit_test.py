# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_test.ui'
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


class Ui_EditTestDialog(object):
    def setupUi(self, EditTestDialog):
        if not EditTestDialog.objectName():
            EditTestDialog.setObjectName(u"EditTestDialog")
        EditTestDialog.resize(1020, 767)
        self.verticalLayout_6 = QVBoxLayout(EditTestDialog)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(EditTestDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.form = QFormLayout()
        self.form.setObjectName(u"form")
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.setVerticalSpacing(6)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.form.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.curveNameLineEdit = QLineEdit(self.groupBox)
        self.curveNameLineEdit.setObjectName(u"curveNameLineEdit")

        self.form.setWidget(0, QFormLayout.ItemRole.FieldRole, self.curveNameLineEdit)

        self.colorLabel = QLabel(self.groupBox)
        self.colorLabel.setObjectName(u"colorLabel")

        self.form.setWidget(1, QFormLayout.ItemRole.LabelRole, self.colorLabel)

        self.colorButton = ColorButton(self.groupBox)
        self.colorButton.setObjectName(u"colorButton")
        self.colorButton.setMaximumSize(QSize(30, 30))
        self.colorButton.setStyleSheet(u"background-color: transparent;")
        self.colorButton.setAutoDefault(False)

        self.form.setWidget(1, QFormLayout.ItemRole.FieldRole, self.colorButton)

        self.lineTypeLabel = QLabel(self.groupBox)
        self.lineTypeLabel.setObjectName(u"lineTypeLabel")

        self.form.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lineTypeLabel)

        self.lineType = QComboBox(self.groupBox)
        self.lineType.setObjectName(u"lineType")
        self.lineType.setMinimumSize(QSize(200, 0))

        self.form.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineType)

        self.thicknessLabel = QLabel(self.groupBox)
        self.thicknessLabel.setObjectName(u"thicknessLabel")

        self.form.setWidget(3, QFormLayout.ItemRole.LabelRole, self.thicknessLabel)

        self.thickness = QSpinBox(self.groupBox)
        self.thickness.setObjectName(u"thickness")
        self.thickness.setValue(1)

        self.form.setWidget(3, QFormLayout.ItemRole.FieldRole, self.thickness)

        self.pointTypeLabel = QLabel(self.groupBox)
        self.pointTypeLabel.setObjectName(u"pointTypeLabel")

        self.form.setWidget(4, QFormLayout.ItemRole.LabelRole, self.pointTypeLabel)

        self.pointType = QComboBox(self.groupBox)
        self.pointType.setObjectName(u"pointType")

        self.form.setWidget(4, QFormLayout.ItemRole.FieldRole, self.pointType)

        self.pointSizeLabel = QLabel(self.groupBox)
        self.pointSizeLabel.setObjectName(u"pointSizeLabel")

        self.form.setWidget(5, QFormLayout.ItemRole.LabelRole, self.pointSizeLabel)

        self.pointSizeSpinBox = QSpinBox(self.groupBox)
        self.pointSizeSpinBox.setObjectName(u"pointSizeSpinBox")
        self.pointSizeSpinBox.setValue(10)

        self.form.setWidget(5, QFormLayout.ItemRole.FieldRole, self.pointSizeSpinBox)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.form.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.colorButton_3 = ColorButton(self.groupBox)
        self.colorButton_3.setObjectName(u"colorButton_3")
        self.colorButton_3.setMaximumSize(QSize(30, 30))
        self.colorButton_3.setStyleSheet(u"background-color: transparent;")
        self.colorButton_3.setAutoDefault(False)

        self.form.setWidget(6, QFormLayout.ItemRole.FieldRole, self.colorButton_3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.form.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.colorButton_2 = ColorButton(self.groupBox)
        self.colorButton_2.setObjectName(u"colorButton_2")
        self.colorButton_2.setMaximumSize(QSize(30, 30))
        self.colorButton_2.setStyleSheet(u"background-color: transparent;")
        self.colorButton_2.setAutoDefault(False)

        self.form.setWidget(7, QFormLayout.ItemRole.FieldRole, self.colorButton_2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.form.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.displayCheckBox = QCheckBox(self.groupBox)
        self.displayCheckBox.setObjectName(u"displayCheckBox")

        self.form.setWidget(8, QFormLayout.ItemRole.FieldRole, self.displayCheckBox)


        self.horizontalLayout.addLayout(self.form)

        self.plotView = PlotWidget(self.groupBox)
        self.plotView.setObjectName(u"plotView")
        self.plotView.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.plotView)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(EditTestDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.groupBox_3 = QGroupBox(self.groupBox_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(self.groupBox_3)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 462, 286))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.addConditionButton = QPushButton(self.groupBox_3)
        self.addConditionButton.setObjectName(u"addConditionButton")

        self.verticalLayout_3.addWidget(self.addConditionButton)

        self.applyCheckBox = QCheckBox(self.groupBox_3)
        self.applyCheckBox.setObjectName(u"applyCheckBox")

        self.verticalLayout_3.addWidget(self.applyCheckBox)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.copyButton = QPushButton(self.groupBox_3)
        self.copyButton.setObjectName(u"copyButton")

        self.horizontalLayout_3.addWidget(self.copyButton)

        self.pasteButton = QPushButton(self.groupBox_3)
        self.pasteButton.setObjectName(u"pasteButton")

        self.horizontalLayout_3.addWidget(self.pasteButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.horizontalLayout_6.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_4 = QGridLayout(self.groupBox_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea_2 = QScrollArea(self.groupBox_4)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 462, 286))
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_4.addWidget(self.scrollArea_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.addConditionButton_2 = QPushButton(self.groupBox_4)
        self.addConditionButton_2.setObjectName(u"addConditionButton_2")

        self.verticalLayout_5.addWidget(self.addConditionButton_2)

        self.applyCheckBox_2 = QCheckBox(self.groupBox_4)
        self.applyCheckBox_2.setObjectName(u"applyCheckBox_2")

        self.verticalLayout_5.addWidget(self.applyCheckBox_2)


        self.horizontalLayout_4.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.copyButton_2 = QPushButton(self.groupBox_4)
        self.copyButton_2.setObjectName(u"copyButton_2")

        self.horizontalLayout_5.addWidget(self.copyButton_2)

        self.pasteButton_2 = QPushButton(self.groupBox_4)
        self.pasteButton_2.setObjectName(u"pasteButton_2")

        self.horizontalLayout_5.addWidget(self.pasteButton_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)


        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)


        self.horizontalLayout_6.addWidget(self.groupBox_4)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.buttonBox = QDialogButtonBox(EditTestDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.verticalLayout_6.addLayout(self.verticalLayout)


        self.retranslateUi(EditTestDialog)
        self.buttonBox.accepted.connect(EditTestDialog.accept)
        self.buttonBox.rejected.connect(EditTestDialog.reject)

        QMetaObject.connectSlotsByName(EditTestDialog)
    # setupUi

    def retranslateUi(self, EditTestDialog):
        EditTestDialog.setWindowTitle(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u043a\u0440\u0438\u0432\u043e\u0439", None))
        self.label.setText(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0440\u0438\u0432\u043e\u0439:", None))
        self.colorLabel.setText(QCoreApplication.translate("EditTestDialog", u"\u0426\u0432\u0435\u0442 \u043b\u0438\u043d\u0438\u0438", None))
        self.lineTypeLabel.setText(QCoreApplication.translate("EditTestDialog", u"\u0422\u0438\u043f \u043b\u0438\u043d\u0438\u0438", None))
        self.thicknessLabel.setText(QCoreApplication.translate("EditTestDialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None))
        self.pointTypeLabel.setText(QCoreApplication.translate("EditTestDialog", u"\u0412\u0438\u0434 \u0442\u043e\u0447\u043a\u0438", None))
        self.pointSizeLabel.setText(QCoreApplication.translate("EditTestDialog", u"\u0420\u0430\u0437\u043c\u0435\u0440 \u0442\u043e\u0447\u043a\u0438", None))
        self.label_3.setText(QCoreApplication.translate("EditTestDialog", u"\u0426\u0432\u0435\u0442 \u0433\u0440\u0430\u043d\u0438\u0446\u044b \u0442\u043e\u0447\u043a\u0438", None))
        self.label_4.setText(QCoreApplication.translate("EditTestDialog", u"\u0417\u0430\u043b\u0438\u0432\u043a\u0430 \u0442\u043e\u0447\u043a\u0438", None))
        self.label_2.setText(QCoreApplication.translate("EditTestDialog", u"\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430\u0445", None))
        self.displayCheckBox.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0443\u0441\u043b\u043e\u0432\u0438\u0439", None))
        self.addConditionButton.setText(QCoreApplication.translate("EditTestDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u0435", None))
        self.applyCheckBox.setText(QCoreApplication.translate("EditTestDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f", None))
        self.copyButton.setText(QCoreApplication.translate("EditTestDialog", u"\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f", None))
        self.pasteButton.setText(QCoreApplication.translate("EditTestDialog", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("EditTestDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0444\u0438\u043b\u044c\u0442\u0440\u0430\u0446\u0438\u0438", None))
        self.addConditionButton_2.setText(QCoreApplication.translate("EditTestDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0444\u0438\u043b\u044c\u0442\u0440", None))
        self.applyCheckBox_2.setText(QCoreApplication.translate("EditTestDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c \u0444\u0438\u043b\u044c\u0442\u0440\u0430\u0446\u0438\u044e", None))
        self.copyButton_2.setText(QCoreApplication.translate("EditTestDialog", u"\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0444\u0438\u043b\u044c\u0442\u0440\u044b", None))
        self.pasteButton_2.setText(QCoreApplication.translate("EditTestDialog", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0444\u0438\u043b\u044c\u0442\u0440\u044b", None))
    # retranslateUi

