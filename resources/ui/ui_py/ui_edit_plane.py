# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_plane.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_EditPlaneDialog(object):
    def setupUi(self, EditPlaneDialog):
        if not EditPlaneDialog.objectName():
            EditPlaneDialog.setObjectName(u"EditPlaneDialog")
        EditPlaneDialog.resize(548, 682)
        self.gridLayout_6 = QGridLayout(EditPlaneDialog)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_11 = QLabel(EditPlaneDialog)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_4.addWidget(self.label_11)

        self.plotName = QLineEdit(EditPlaneDialog)
        self.plotName.setObjectName(u"plotName")

        self.horizontalLayout_4.addWidget(self.plotName)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.verticalLayout_12.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.xAxisGroup = QGroupBox(EditPlaneDialog)
        self.xAxisGroup.setObjectName(u"xAxisGroup")
        self.verticalLayout = QVBoxLayout(self.xAxisGroup)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.xAxisFixed = QCheckBox(self.xAxisGroup)
        self.xAxisFixed.setObjectName(u"xAxisFixed")

        self.gridLayout.addWidget(self.xAxisFixed, 3, 0, 1, 2)

        self.label = QLabel(self.xAxisGroup)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_8 = QLabel(self.xAxisGroup)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_2.addWidget(self.label_8)

        self.xMin = QLineEdit(self.xAxisGroup)
        self.xMin.setObjectName(u"xMin")

        self.horizontalLayout_2.addWidget(self.xMin)

        self.label_9 = QLabel(self.xAxisGroup)
        self.label_9.setObjectName(u"label_9")

        self.horizontalLayout_2.addWidget(self.label_9)

        self.xMax = QLineEdit(self.xAxisGroup)
        self.xMax.setObjectName(u"xMax")

        self.horizontalLayout_2.addWidget(self.xMax)

        self.label_10 = QLabel(self.xAxisGroup)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_2.addWidget(self.label_10)


        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)

        self.label_12 = QLabel(self.xAxisGroup)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.label_12, 5, 0, 1, 1)

        self.line = QFrame(self.xAxisGroup)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)

        self.label_4 = QLabel(self.xAxisGroup)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.xGridAuto = QRadioButton(self.xAxisGroup)
        self.xGridMode = QButtonGroup(EditPlaneDialog)
        self.xGridMode.setObjectName(u"xGridMode")
        self.xGridMode.addButton(self.xGridAuto)
        self.xGridAuto.setObjectName(u"xGridAuto")

        self.verticalLayout_4.addWidget(self.xGridAuto)

        self.xGridManually = QRadioButton(self.xAxisGroup)
        self.xGridMode.addButton(self.xGridManually)
        self.xGridManually.setObjectName(u"xGridManually")

        self.verticalLayout_4.addWidget(self.xGridManually)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(6)
        self.gridLayout_3.setVerticalSpacing(2)
        self.xMajor = QDoubleSpinBox(self.xAxisGroup)
        self.xMajor.setObjectName(u"xMajor")
        self.xMajor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.xMajor.setDecimals(4)
        self.xMajor.setMaximum(1000.000000000000000)

        self.gridLayout_3.addWidget(self.xMajor, 0, 1, 1, 1)

        self.label_14 = QLabel(self.xAxisGroup)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_3.addWidget(self.label_14, 0, 0, 1, 1)

        self.label_15 = QLabel(self.xAxisGroup)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_3.addWidget(self.label_15, 1, 0, 1, 1)

        self.xMinor = QDoubleSpinBox(self.xAxisGroup)
        self.xMinor.setObjectName(u"xMinor")
        self.xMinor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.xMinor.setDecimals(4)
        self.xMinor.setMaximum(1000.000000000000000)

        self.gridLayout_3.addWidget(self.xMinor, 1, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_3)


        self.gridLayout.addLayout(self.verticalLayout_4, 5, 1, 1, 1)

        self.xAxisName = QLineEdit(self.xAxisGroup)
        self.xAxisName.setObjectName(u"xAxisName")

        self.gridLayout.addWidget(self.xAxisName, 0, 1, 1, 1)

        self.label_24 = QLabel(self.xAxisGroup)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout.addWidget(self.label_24, 1, 0, 1, 1)

        self.lineEdit = QLineEdit(self.xAxisGroup)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)


        self.verticalLayout_11.addWidget(self.xAxisGroup)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_23 = QLabel(EditPlaneDialog)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_23.setWordWrap(True)

        self.verticalLayout_10.addWidget(self.label_23)

        self.defaultRadioButton = QRadioButton(EditPlaneDialog)
        self.defaultRadioButton.setObjectName(u"defaultRadioButton")
        self.defaultRadioButton.setChecked(True)

        self.verticalLayout_10.addWidget(self.defaultRadioButton)

        self.assemblyRadioButton = QRadioButton(EditPlaneDialog)
        self.assemblyRadioButton.setObjectName(u"assemblyRadioButton")

        self.verticalLayout_10.addWidget(self.assemblyRadioButton)

        self.modelRadioButton = QRadioButton(EditPlaneDialog)
        self.modelRadioButton.setObjectName(u"modelRadioButton")

        self.verticalLayout_10.addWidget(self.modelRadioButton)

        self.productRadioButton = QRadioButton(EditPlaneDialog)
        self.productRadioButton.setObjectName(u"productRadioButton")

        self.verticalLayout_10.addWidget(self.productRadioButton)

        self.groupBox = QGroupBox(EditPlaneDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_25 = QLabel(self.groupBox)
        self.label_25.setObjectName(u"label_25")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_25)

        self.label_26 = QLabel(self.groupBox)
        self.label_26.setObjectName(u"label_26")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_26)

        self.xMultiplier = QDoubleSpinBox(self.groupBox)
        self.xMultiplier.setObjectName(u"xMultiplier")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.xMultiplier)

        self.yMultiplier = QDoubleSpinBox(self.groupBox)
        self.yMultiplier.setObjectName(u"yMultiplier")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.yMultiplier)


        self.gridLayout_4.addLayout(self.formLayout_2, 0, 0, 1, 1)

        self.formLayout_4 = QFormLayout()
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_28 = QLabel(self.groupBox)
        self.label_28.setObjectName(u"label_28")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_28)

        self.label_29 = QLabel(self.groupBox)
        self.label_29.setObjectName(u"label_29")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_29)

        self.xD = QDoubleSpinBox(self.groupBox)
        self.xD.setObjectName(u"xD")

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.xD)

        self.yD = QDoubleSpinBox(self.groupBox)
        self.yD.setObjectName(u"yD")

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.yD)


        self.gridLayout_4.addLayout(self.formLayout_4, 1, 0, 1, 1)


        self.verticalLayout_10.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)


        self.verticalLayout_11.addLayout(self.verticalLayout_10)


        self.horizontalLayout_5.addLayout(self.verticalLayout_11)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.yAxisGroup = QGroupBox(EditPlaneDialog)
        self.yAxisGroup.setObjectName(u"yAxisGroup")
        self.verticalLayout_3 = QVBoxLayout(self.yAxisGroup)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_13 = QLabel(self.yAxisGroup)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout_2.addWidget(self.label_13, 5, 0, 1, 1)

        self.line_2 = QFrame(self.yAxisGroup)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 4, 0, 1, 2)

        self.label_2 = QLabel(self.yAxisGroup)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.yAxisFixed = QCheckBox(self.yAxisGroup)
        self.yAxisFixed.setObjectName(u"yAxisFixed")

        self.gridLayout_2.addWidget(self.yAxisFixed, 3, 0, 1, 2)

        self.label_3 = QLabel(self.yAxisGroup)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.yGridAuto = QRadioButton(self.yAxisGroup)
        self.yGridMode = QButtonGroup(EditPlaneDialog)
        self.yGridMode.setObjectName(u"yGridMode")
        self.yGridMode.addButton(self.yGridAuto)
        self.yGridAuto.setObjectName(u"yGridAuto")

        self.verticalLayout_5.addWidget(self.yGridAuto)

        self.yGridManually = QRadioButton(self.yAxisGroup)
        self.yGridMode.addButton(self.yGridManually)
        self.yGridManually.setObjectName(u"yGridManually")

        self.verticalLayout_5.addWidget(self.yGridManually)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setVerticalSpacing(2)
        self.label_16 = QLabel(self.yAxisGroup)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_5.addWidget(self.label_16, 0, 0, 1, 1)

        self.label_17 = QLabel(self.yAxisGroup)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_5.addWidget(self.label_17, 1, 0, 1, 1)

        self.yMajor = QDoubleSpinBox(self.yAxisGroup)
        self.yMajor.setObjectName(u"yMajor")
        font = QFont()
        font.setKerning(True)
        self.yMajor.setFont(font)
        self.yMajor.setWrapping(False)
        self.yMajor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.yMajor.setAccelerated(False)
        self.yMajor.setCorrectionMode(QAbstractSpinBox.CorrectToPreviousValue)
        self.yMajor.setKeyboardTracking(True)
        self.yMajor.setProperty("showGroupSeparator", False)
        self.yMajor.setDecimals(4)
        self.yMajor.setMaximum(1000.000000000000000)
        self.yMajor.setValue(0.000000000000000)

        self.gridLayout_5.addWidget(self.yMajor, 0, 1, 1, 1)

        self.yMinor = QDoubleSpinBox(self.yAxisGroup)
        self.yMinor.setObjectName(u"yMinor")
        self.yMinor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.yMinor.setDecimals(4)
        self.yMinor.setMaximum(1000.000000000000000)

        self.gridLayout_5.addWidget(self.yMinor, 1, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_5)


        self.gridLayout_2.addLayout(self.verticalLayout_5, 5, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_6 = QLabel(self.yAxisGroup)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)

        self.yMin = QLineEdit(self.yAxisGroup)
        self.yMin.setObjectName(u"yMin")

        self.horizontalLayout.addWidget(self.yMin)

        self.label_5 = QLabel(self.yAxisGroup)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout.addWidget(self.label_5)

        self.yMax = QLineEdit(self.yAxisGroup)
        self.yMax.setObjectName(u"yMax")

        self.horizontalLayout.addWidget(self.yMax)

        self.label_7 = QLabel(self.yAxisGroup)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout.addWidget(self.label_7)


        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 1, 1, 1)

        self.yAxisName = QLineEdit(self.yAxisGroup)
        self.yAxisName.setObjectName(u"yAxisName")

        self.gridLayout_2.addWidget(self.yAxisName, 0, 1, 1, 1)

        self.label_27 = QLabel(self.yAxisGroup)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout_2.addWidget(self.label_27, 1, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.yAxisGroup)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout_2.addWidget(self.lineEdit_2, 1, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_2)


        self.verticalLayout_2.addWidget(self.yAxisGroup)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_18 = QLabel(EditPlaneDialog)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.label_18)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_19 = QLabel(EditPlaneDialog)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_19)

        self.comboBox = QComboBox(EditPlaneDialog)
        self.comboBox.setObjectName(u"comboBox")

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.comboBox)


        self.verticalLayout_6.addLayout(self.formLayout_5)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_20 = QLabel(EditPlaneDialog)
        self.label_20.setObjectName(u"label_20")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_20)

        self.fromDoubleSpinBox = QDoubleSpinBox(EditPlaneDialog)
        self.fromDoubleSpinBox.setObjectName(u"fromDoubleSpinBox")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.fromDoubleSpinBox)

        self.label_21 = QLabel(EditPlaneDialog)
        self.label_21.setObjectName(u"label_21")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_21)

        self.toDoubleSpinBox = QDoubleSpinBox(EditPlaneDialog)
        self.toDoubleSpinBox.setObjectName(u"toDoubleSpinBox")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.toDoubleSpinBox)


        self.verticalLayout_7.addLayout(self.formLayout_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.acceptPushButton = QPushButton(EditPlaneDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout_3.addWidget(self.acceptPushButton)

        self.deletePushButton = QPushButton(EditPlaneDialog)
        self.deletePushButton.setObjectName(u"deletePushButton")

        self.horizontalLayout_3.addWidget(self.deletePushButton)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)


        self.verticalLayout_6.addLayout(self.verticalLayout_7)


        self.verticalLayout_8.addLayout(self.verticalLayout_6)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_22 = QLabel(EditPlaneDialog)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setWordWrap(True)

        self.verticalLayout_9.addWidget(self.label_22)

        self.listWidget = QListWidget(EditPlaneDialog)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout_9.addWidget(self.listWidget)


        self.verticalLayout_8.addLayout(self.verticalLayout_9)


        self.verticalLayout_2.addLayout(self.verticalLayout_8)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)


        self.verticalLayout_12.addLayout(self.horizontalLayout_5)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.buttonLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.cancelButton = QPushButton(EditPlaneDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.buttonLayout.addWidget(self.cancelButton)

        self.okButton = QPushButton(EditPlaneDialog)
        self.okButton.setObjectName(u"okButton")
        self.okButton.setEnabled(True)

        self.buttonLayout.addWidget(self.okButton)


        self.verticalLayout_12.addLayout(self.buttonLayout)


        self.gridLayout_6.addLayout(self.verticalLayout_12, 0, 0, 1, 1)


        self.retranslateUi(EditPlaneDialog)

        self.cancelButton.setDefault(False)
        self.okButton.setDefault(True)


        QMetaObject.connectSlotsByName(EditPlaneDialog)
    # setupUi

    def retranslateUi(self, EditPlaneDialog):
        EditPlaneDialog.setWindowTitle(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.label_11.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0430\u0444\u0438\u043a\u0430:", None))
        self.xAxisGroup.setTitle(QCoreApplication.translate("EditPlaneDialog", u"\u0413\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0441\u044c", None))
        self.xAxisFixed.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0417\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b", None))
        self.label.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.label_8.setText(QCoreApplication.translate("EditPlaneDialog", u"[", None))
        self.xMin.setPlaceholderText(QCoreApplication.translate("EditPlaneDialog", u"\u043e\u0442", None))
        self.label_9.setText(QCoreApplication.translate("EditPlaneDialog", u":", None))
        self.xMax.setPlaceholderText(QCoreApplication.translate("EditPlaneDialog", u"\u0434\u043e", None))
        self.label_10.setText(QCoreApplication.translate("EditPlaneDialog", u"]", None))
        self.label_12.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0428\u0430\u0433 \u0441\u0435\u0442\u043a\u0438:", None))
        self.label_4.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b:", None))
        self.xGridAuto.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438", None))
        self.xGridManually.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0412\u0440\u0443\u0447\u043d\u0443\u044e:", None))
        self.label_14.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f", None))
        self.label_15.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f", None))
        self.label_24.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439:", None))
        self.label_23.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0439 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430\u0445 \u043f\u043e \u0433\u0440\u0443\u043f\u043f\u0430\u043c", None))
        self.defaultRadioButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e", None))
        self.assemblyRadioButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0421\u0431\u043e\u0440\u043a\u0430", None))
        self.modelRadioButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041e\u043f\u044b\u0442\u043d\u044b\u0439 \u043e\u0431\u0440\u0430\u0437\u0435\u0446", None))
        self.productRadioButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0418\u0437\u0434\u0435\u043b\u0438\u0435", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditPlaneDialog", u"\u041f\u0435\u0440\u0435\u0445\u043e\u0434 \u0432 \u043e\u0442\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u0432\u0438\u0434", None))
        self.label_25.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c X:", None))
        self.label_26.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c Y:", None))
        self.label_28.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0414\u0435\u043b\u0438\u0442\u0435\u043b\u044c X:", None))
        self.label_29.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0414\u0435\u043b\u0438\u0442\u0435\u043b\u044c Y:", None))
        self.yAxisGroup.setTitle(QCoreApplication.translate("EditPlaneDialog", u"\u0412\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0441\u044c", None))
        self.label_13.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0428\u0430\u0433 \u0441\u0435\u0442\u043a\u0438:", None))
        self.label_2.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.yAxisFixed.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0417\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b", None))
        self.label_3.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b:", None))
        self.yGridAuto.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438", None))
        self.yGridManually.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0412\u0440\u0443\u0447\u043d\u0443\u044e:", None))
        self.label_16.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f", None))
        self.label_17.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u0430\u044f", None))
        self.label_6.setText(QCoreApplication.translate("EditPlaneDialog", u"[", None))
        self.yMin.setPlaceholderText(QCoreApplication.translate("EditPlaneDialog", u"\u043e\u0442", None))
        self.label_5.setText(QCoreApplication.translate("EditPlaneDialog", u":", None))
        self.yMax.setPlaceholderText(QCoreApplication.translate("EditPlaneDialog", u"\u0434\u043e", None))
        self.label_7.setText(QCoreApplication.translate("EditPlaneDialog", u"]", None))
        self.label_27.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041a\u043e\u043c\u043c\u0435\u043d\u0430\u0442\u0440\u0438\u0439:", None))
        self.label_18.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0412\u044b\u0431\u043e\u0440 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430 \u0434\u043b\u044f \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0434\u0438\u0430\u043f\u0430\u0437\u043e\u043d\u0430 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f", None))
        self.label_19.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.label_20.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041e\u0442:", None))
        self.label_21.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0414\u043e:", None))
        self.acceptPushButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.deletePushButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_22.setText(QCoreApplication.translate("EditPlaneDialog", u"\u0421\u043f\u0438\u0441\u043e\u043a \u0437\u0430\u0434\u0430\u043d\u043d\u044b\u0439 \u0443\u0441\u043b\u043e\u0432\u0438\u0439 \u0434\u043b\u044f \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f", None))
        self.cancelButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.okButton.setText(QCoreApplication.translate("EditPlaneDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi

