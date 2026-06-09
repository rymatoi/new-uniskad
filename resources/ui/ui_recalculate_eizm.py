# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'recalculate_eizm.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_RecalculateEizmDialog(object):
    def setupUi(self, RecalculateEizmDialog):
        if not RecalculateEizmDialog.objectName():
            RecalculateEizmDialog.setObjectName(u"RecalculateEizmDialog")
        RecalculateEizmDialog.resize(244, 110)
        self.gridLayout = QGridLayout(RecalculateEizmDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(RecalculateEizmDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.fromComboBox = QComboBox(RecalculateEizmDialog)
        self.fromComboBox.setObjectName(u"fromComboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fromComboBox)

        self.label_2 = QLabel(RecalculateEizmDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.toComboBox = QComboBox(RecalculateEizmDialog)
        self.toComboBox.setObjectName(u"toComboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.toComboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.acceptPushButton = QPushButton(RecalculateEizmDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout.addWidget(self.acceptPushButton)

        self.cancelPushButton = QPushButton(RecalculateEizmDialog)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout.addWidget(self.cancelPushButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(RecalculateEizmDialog)

        QMetaObject.connectSlotsByName(RecalculateEizmDialog)

    # setupUi

    def retranslateUi(self, RecalculateEizmDialog):
        RecalculateEizmDialog.setWindowTitle(QCoreApplication.translate("RecalculateEizmDialog",
                                                                        u"\u041f\u0435\u0440\u0435\u0441\u0447\u0435\u0442 \u0435\u0434\u0438\u043d\u0438\u0446 \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f",
                                                                        None))
        self.label.setText(QCoreApplication.translate("RecalculateEizmDialog", u"\u0418\u0437:", None))
        self.label_2.setText(QCoreApplication.translate("RecalculateEizmDialog", u"\u0412:", None))
        self.acceptPushButton.setText(QCoreApplication.translate("RecalculateEizmDialog",
                                                                 u"\u041f\u0435\u0440\u0435\u0441\u0447\u0438\u0442\u0430\u0442\u044c",
                                                                 None))
        self.cancelPushButton.setText(
            QCoreApplication.translate("RecalculateEizmDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
