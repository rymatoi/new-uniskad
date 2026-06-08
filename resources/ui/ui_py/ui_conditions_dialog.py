# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'conditions_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_AddConditionsDialog(object):
    def setupUi(self, AddConditionsDialog):
        if not AddConditionsDialog.objectName():
            AddConditionsDialog.setObjectName(u"AddConditionsDialog")
        AddConditionsDialog.resize(440, 520)
        self.gridLayout = QGridLayout(AddConditionsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(AddConditionsDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 418, 411))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.addConditionButton = QPushButton(AddConditionsDialog)
        self.addConditionButton.setObjectName(u"addConditionButton")

        self.verticalLayout_3.addWidget(self.addConditionButton)

        self.applyCheckBox = QCheckBox(AddConditionsDialog)
        self.applyCheckBox.setObjectName(u"applyCheckBox")

        self.verticalLayout_3.addWidget(self.applyCheckBox)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.copyButton = QPushButton(AddConditionsDialog)
        self.copyButton.setObjectName(u"copyButton")

        self.horizontalLayout.addWidget(self.copyButton)

        self.pasteButton = QPushButton(AddConditionsDialog)
        self.pasteButton.setObjectName(u"pasteButton")

        self.horizontalLayout.addWidget(self.pasteButton)

        self.cancelButton = QPushButton(AddConditionsDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.acceptButton = QPushButton(AddConditionsDialog)
        self.acceptButton.setObjectName(u"acceptButton")

        self.horizontalLayout.addWidget(self.acceptButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(AddConditionsDialog)

        QMetaObject.connectSlotsByName(AddConditionsDialog)

    # setupUi

    def retranslateUi(self, AddConditionsDialog):
        AddConditionsDialog.setWindowTitle(QCoreApplication.translate("AddConditionsDialog",
                                                                      u"\u041c\u0430\u0440\u043a\u0438\u0440\u043e\u0432\u043a\u0430 \u0442\u043e\u0447\u0435\u043a \u043f\u043e \u0443\u0441\u043b\u043e\u0432\u0438\u044f\u043c",
                                                                      None))
        self.addConditionButton.setText(QCoreApplication.translate("AddConditionsDialog",
                                                                   u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u0435",
                                                                   None))
        self.applyCheckBox.setText(QCoreApplication.translate("AddConditionsDialog",
                                                              u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f",
                                                              None))
        self.copyButton.setText(QCoreApplication.translate("AddConditionsDialog",
                                                           u"\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f",
                                                           None))
        self.pasteButton.setText(QCoreApplication.translate("AddConditionsDialog",
                                                            u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0443\u0441\u043b\u043e\u0432\u0438\u044f",
                                                            None))
        self.cancelButton.setText(
            QCoreApplication.translate("AddConditionsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.acceptButton.setText(QCoreApplication.translate("AddConditionsDialog", u"\u041e\u043a", None))
    # retranslateUi
