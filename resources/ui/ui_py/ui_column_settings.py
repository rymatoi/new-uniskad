# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'column_settings.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_ColumnSettingsDialog(object):
    def setupUi(self, ColumnSettingsDialog):
        if not ColumnSettingsDialog.objectName():
            ColumnSettingsDialog.setObjectName(u"ColumnSettingsDialog")
        ColumnSettingsDialog.resize(323, 73)
        self.gridLayout = QGridLayout(ColumnSettingsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(ColumnSettingsDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.alignComboBox = QComboBox(ColumnSettingsDialog)
        self.alignComboBox.addItem("")
        self.alignComboBox.addItem("")
        self.alignComboBox.addItem("")
        self.alignComboBox.setObjectName(u"alignComboBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.alignComboBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.savePushButton = QPushButton(ColumnSettingsDialog)
        self.savePushButton.setObjectName(u"savePushButton")

        self.horizontalLayout.addWidget(self.savePushButton)

        self.cancelButton = QPushButton(ColumnSettingsDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(ColumnSettingsDialog)

        QMetaObject.connectSlotsByName(ColumnSettingsDialog)

    # setupUi

    def retranslateUi(self, ColumnSettingsDialog):
        ColumnSettingsDialog.setWindowTitle(QCoreApplication.translate("ColumnSettingsDialog",
                                                                       u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0441\u0442\u043e\u043b\u0431\u0446\u0430",
                                                                       None))
        self.label.setText(QCoreApplication.translate("ColumnSettingsDialog",
                                                      u"\u0412\u044b\u0440\u0430\u0432\u043d\u0438\u0432\u0430\u043d\u0438\u0435",
                                                      None))
        self.alignComboBox.setItemText(0, QCoreApplication.translate("ColumnSettingsDialog",
                                                                     u"\u0421\u043b\u0435\u0432\u0430", None))
        self.alignComboBox.setItemText(1, QCoreApplication.translate("ColumnSettingsDialog",
                                                                     u"\u041f\u043e \u0446\u0435\u043d\u0442\u0440\u0443",
                                                                     None))
        self.alignComboBox.setItemText(2, QCoreApplication.translate("ColumnSettingsDialog",
                                                                     u"\u0421\u043f\u0440\u0430\u0432\u0430", None))

        self.savePushButton.setText(QCoreApplication.translate("ColumnSettingsDialog",
                                                               u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
                                                               None))
        self.cancelButton.setText(
            QCoreApplication.translate("ColumnSettingsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
