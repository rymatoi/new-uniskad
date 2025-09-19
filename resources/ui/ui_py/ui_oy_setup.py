# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'oy_setup.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_OYSetupDialog(object):
    def setupUi(self, OYSetupDialog):
        if not OYSetupDialog.objectName():
            OYSetupDialog.setObjectName(u"OYSetupDialog")
        OYSetupDialog.resize(178, 464)
        self.gridLayout = QGridLayout(OYSetupDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableWidget = QTableWidget(OYSetupDialog)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout.addWidget(self.tableWidget)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.acceptButton = QPushButton(OYSetupDialog)
        self.acceptButton.setObjectName(u"acceptButton")

        self.horizontalLayout.addWidget(self.acceptButton)

        self.cancelButton = QPushButton(OYSetupDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(OYSetupDialog)

        QMetaObject.connectSlotsByName(OYSetupDialog)

    # setupUi

    def retranslateUi(self, OYSetupDialog):
        OYSetupDialog.setWindowTitle(
            QCoreApplication.translate("OYSetupDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 OY",
                                       None))
        self.acceptButton.setText(QCoreApplication.translate("OYSetupDialog", u"\u041e\u043a", None))
        self.cancelButton.setText(
            QCoreApplication.translate("OYSetupDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
