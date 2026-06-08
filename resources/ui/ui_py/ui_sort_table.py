# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sort_table.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_SortDialog(object):
    def setupUi(self, SortDialog):
        if not SortDialog.objectName():
            SortDialog.setObjectName(u"SortDialog")
        SortDialog.resize(400, 174)
        self.gridLayout = QGridLayout(SortDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(SortDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.escRadioButton = QRadioButton(SortDialog)
        self.escRadioButton.setObjectName(u"escRadioButton")

        self.verticalLayout.addWidget(self.escRadioButton)

        self.descRadioButton = QRadioButton(SortDialog)
        self.descRadioButton.setObjectName(u"descRadioButton")

        self.verticalLayout.addWidget(self.descRadioButton)

        self.offRadioButton = QRadioButton(SortDialog)
        self.offRadioButton.setObjectName(u"offRadioButton")

        self.verticalLayout.addWidget(self.offRadioButton)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.saveButton = QPushButton(SortDialog)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.cancelButton = QPushButton(SortDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(SortDialog)

        QMetaObject.connectSlotsByName(SortDialog)

    # setupUi

    def retranslateUi(self, SortDialog):
        SortDialog.setWindowTitle(
            QCoreApplication.translate("SortDialog", u"\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430",
                                       None))
        self.label.setText(QCoreApplication.translate("SortDialog",
                                                      u"\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u043e\u0432:",
                                                      None))
        self.escRadioButton.setText(QCoreApplication.translate("SortDialog", u"\u0410-\u042f", None))
        self.descRadioButton.setText(QCoreApplication.translate("SortDialog", u"\u042f-\u0410", None))
        self.offRadioButton.setText(QCoreApplication.translate("SortDialog",
                                                               u"\u0411\u0435\u0437 \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438",
                                                               None))
        self.saveButton.setText(
            QCoreApplication.translate("SortDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.cancelButton.setText(
            QCoreApplication.translate("SortDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
