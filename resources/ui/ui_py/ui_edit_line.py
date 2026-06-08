# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_line.ui'
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


class Ui_EditLineDialog(object):
    def setupUi(self, EditLineDialog):
        if not EditLineDialog.objectName():
            EditLineDialog.setObjectName(u"EditLineDialog")
        EditLineDialog.resize(630, 297)
        self.verticalLayout_6 = QVBoxLayout(EditLineDialog)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(EditLineDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.form = QFormLayout()
        self.form.setObjectName(u"form")
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.form.setVerticalSpacing(6)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.form.setWidget(0, QFormLayout.LabelRole, self.label)

        self.curveNameLineEdit = QLineEdit(self.groupBox)
        self.curveNameLineEdit.setObjectName(u"curveNameLineEdit")

        self.form.setWidget(0, QFormLayout.FieldRole, self.curveNameLineEdit)

        self.colorLabel = QLabel(self.groupBox)
        self.colorLabel.setObjectName(u"colorLabel")

        self.form.setWidget(1, QFormLayout.LabelRole, self.colorLabel)

        self.colorButton = ColorButton(self.groupBox)
        self.colorButton.setObjectName(u"colorButton")
        self.colorButton.setMaximumSize(QSize(30, 30))
        self.colorButton.setStyleSheet(u"background-color: transparent;")
        self.colorButton.setAutoDefault(False)

        self.form.setWidget(1, QFormLayout.FieldRole, self.colorButton)

        self.lineTypeLabel = QLabel(self.groupBox)
        self.lineTypeLabel.setObjectName(u"lineTypeLabel")

        self.form.setWidget(2, QFormLayout.LabelRole, self.lineTypeLabel)

        self.lineType = QComboBox(self.groupBox)
        self.lineType.setObjectName(u"lineType")
        self.lineType.setMinimumSize(QSize(200, 0))

        self.form.setWidget(2, QFormLayout.FieldRole, self.lineType)

        self.thicknessLabel = QLabel(self.groupBox)
        self.thicknessLabel.setObjectName(u"thicknessLabel")

        self.form.setWidget(3, QFormLayout.LabelRole, self.thicknessLabel)

        self.thickness = QSpinBox(self.groupBox)
        self.thickness.setObjectName(u"thickness")
        self.thickness.setValue(1)

        self.form.setWidget(3, QFormLayout.FieldRole, self.thickness)

        self.pointTypeLabel = QLabel(self.groupBox)
        self.pointTypeLabel.setObjectName(u"pointTypeLabel")

        self.form.setWidget(4, QFormLayout.LabelRole, self.pointTypeLabel)

        self.pointType = QComboBox(self.groupBox)
        self.pointType.setObjectName(u"pointType")

        self.form.setWidget(4, QFormLayout.FieldRole, self.pointType)

        self.pointSizeLabel = QLabel(self.groupBox)
        self.pointSizeLabel.setObjectName(u"pointSizeLabel")

        self.form.setWidget(5, QFormLayout.LabelRole, self.pointSizeLabel)

        self.pointSizeSpinBox = QSpinBox(self.groupBox)
        self.pointSizeSpinBox.setObjectName(u"pointSizeSpinBox")
        self.pointSizeSpinBox.setValue(10)

        self.form.setWidget(5, QFormLayout.FieldRole, self.pointSizeSpinBox)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.form.setWidget(6, QFormLayout.LabelRole, self.label_3)

        self.colorButton_3 = ColorButton(self.groupBox)
        self.colorButton_3.setObjectName(u"colorButton_3")
        self.colorButton_3.setMaximumSize(QSize(30, 30))
        self.colorButton_3.setStyleSheet(u"background-color: transparent;")
        self.colorButton_3.setAutoDefault(False)

        self.form.setWidget(6, QFormLayout.FieldRole, self.colorButton_3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.form.setWidget(7, QFormLayout.LabelRole, self.label_4)

        self.colorButton_2 = ColorButton(self.groupBox)
        self.colorButton_2.setObjectName(u"colorButton_2")
        self.colorButton_2.setMaximumSize(QSize(30, 30))
        self.colorButton_2.setStyleSheet(u"background-color: transparent;")
        self.colorButton_2.setAutoDefault(False)

        self.form.setWidget(7, QFormLayout.FieldRole, self.colorButton_2)


        self.horizontalLayout.addLayout(self.form)

        self.plotView = PlotWidget(self.groupBox)
        self.plotView.setObjectName(u"plotView")
        self.plotView.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.plotView)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.buttonBox = QDialogButtonBox(EditLineDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.verticalLayout_6.addLayout(self.verticalLayout)


        self.retranslateUi(EditLineDialog)
        self.buttonBox.accepted.connect(EditLineDialog.accept)
        self.buttonBox.rejected.connect(EditLineDialog.reject)

        QMetaObject.connectSlotsByName(EditLineDialog)
    # setupUi

    def retranslateUi(self, EditLineDialog):
        EditLineDialog.setWindowTitle(QCoreApplication.translate("EditLineDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043b\u0438\u043d\u0438\u0438", None))
        self.groupBox.setTitle(QCoreApplication.translate("EditLineDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f \u043a\u0440\u0438\u0432\u043e\u0439", None))
        self.label.setText(QCoreApplication.translate("EditLineDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0440\u0438\u0432\u043e\u0439:", None))
        self.colorLabel.setText(QCoreApplication.translate("EditLineDialog", u"\u0426\u0432\u0435\u0442 \u043b\u0438\u043d\u0438\u0438", None))
        self.lineTypeLabel.setText(QCoreApplication.translate("EditLineDialog", u"\u0422\u0438\u043f \u043b\u0438\u043d\u0438\u0438", None))
        self.thicknessLabel.setText(QCoreApplication.translate("EditLineDialog", u"\u0422\u043e\u043b\u0449\u0438\u043d\u0430", None))
        self.pointTypeLabel.setText(QCoreApplication.translate("EditLineDialog", u"\u0412\u0438\u0434 \u0442\u043e\u0447\u043a\u0438", None))
        self.pointSizeLabel.setText(QCoreApplication.translate("EditLineDialog", u"\u0420\u0430\u0437\u043c\u0435\u0440 \u0442\u043e\u0447\u043a\u0438", None))
        self.label_3.setText(QCoreApplication.translate("EditLineDialog", u"\u0426\u0432\u0435\u0442 \u0433\u0440\u0430\u043d\u0438\u0446\u044b \u0442\u043e\u0447\u043a\u0438", None))
        self.label_4.setText(QCoreApplication.translate("EditLineDialog", u"\u0417\u0430\u043b\u0438\u0432\u043a\u0430 \u0442\u043e\u0447\u043a\u0438", None))
    # retranslateUi

