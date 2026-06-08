# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'extra_param_epure.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_ExtraParamEoure(object):
    def setupUi(self, ExtraParamEoure):
        if not ExtraParamEoure.objectName():
            ExtraParamEoure.setObjectName(u"ExtraParamEoure")
        ExtraParamEoure.resize(312, 393)
        self.gridLayout = QGridLayout(ExtraParamEoure)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.comboBox = QComboBox(ExtraParamEoure)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout.addWidget(self.comboBox)

        self.label_2 = QLabel(ExtraParamEoure)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.treeWidget = QTreeWidget(ExtraParamEoure)
        self.treeWidget.setObjectName(u"treeWidget")

        self.verticalLayout.addWidget(self.treeWidget)

        self.buttonBox = QDialogButtonBox(ExtraParamEoure)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(ExtraParamEoure)

        QMetaObject.connectSlotsByName(ExtraParamEoure)
    # setupUi

    def retranslateUi(self, ExtraParamEoure):
        ExtraParamEoure.setWindowTitle(QCoreApplication.translate("ExtraParamEoure", u"\u0412\u044b\u0431\u043e\u0440 \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430", None))
        self.label_2.setText(QCoreApplication.translate("ExtraParamEoure", u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f", None))
    # retranslateUi

