# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graph_param_constraint.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GraphParamConstraintDialog(object):
    def setupUi(self, GraphParamConstraintDialog):
        if not GraphParamConstraintDialog.objectName():
            GraphParamConstraintDialog.setObjectName(u"GraphParamConstraintDialog")
        GraphParamConstraintDialog.resize(244, 110)
        self.gridLayout = QGridLayout(GraphParamConstraintDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(GraphParamConstraintDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.fromComboBox = QComboBox(GraphParamConstraintDialog)
        self.fromComboBox.setObjectName(u"fromComboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.fromComboBox)

        self.label_2 = QLabel(GraphParamConstraintDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.toComboBox = QComboBox(GraphParamConstraintDialog)
        self.toComboBox.setObjectName(u"toComboBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.toComboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.acceptPushButton = QPushButton(GraphParamConstraintDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout.addWidget(self.acceptPushButton)

        self.cancelPushButton = QPushButton(GraphParamConstraintDialog)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout.addWidget(self.cancelPushButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(GraphParamConstraintDialog)

        QMetaObject.connectSlotsByName(GraphParamConstraintDialog)

    # setupUi

    def retranslateUi(self, GraphParamConstraintDialog):
        GraphParamConstraintDialog.setWindowTitle(QCoreApplication.translate("GraphParamConstraintDialog",
                                                                             u"\u0412\u044b\u0431\u043e\u0440\u0430 \u0434\u0438\u0430\u043f\u0430\u0437\u043e\u043d\u0430 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0439",
                                                                             None))
        self.label.setText(QCoreApplication.translate("GraphParamConstraintDialog", u"\u041e\u0442:", None))
        self.label_2.setText(QCoreApplication.translate("GraphParamConstraintDialog", u"\u0414\u043e:", None))
        self.acceptPushButton.setText(
            QCoreApplication.translate("GraphParamConstraintDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c",
                                       None))
        self.cancelPushButton.setText(
            QCoreApplication.translate("GraphParamConstraintDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
