# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'version_control_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_VersionControlDialog(object):
    def setupUi(self, VersionControlDialog):
        if not VersionControlDialog.objectName():
            VersionControlDialog.setObjectName(u"VersionControlDialog")
        VersionControlDialog.resize(445, 121)
        self.gridLayout = QGridLayout(VersionControlDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(VersionControlDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_2 = QLabel(VersionControlDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.descriptionEdit = QTextEdit(VersionControlDialog)
        self.descriptionEdit.setObjectName(u"descriptionEdit")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.descriptionEdit)

        self.versionComboBox = QComboBox(VersionControlDialog)
        self.versionComboBox.setObjectName(u"versionComboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.versionComboBox)

        self.horizontalLayout.addLayout(self.formLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.saveButton = QPushButton(VersionControlDialog)
        self.saveButton.setObjectName(u"saveButton")

        self.verticalLayout.addWidget(self.saveButton)

        self.newButton = QPushButton(VersionControlDialog)
        self.newButton.setObjectName(u"newButton")

        self.verticalLayout.addWidget(self.newButton)

        self.removeButton = QPushButton(VersionControlDialog)
        self.removeButton.setObjectName(u"removeButton")

        self.verticalLayout.addWidget(self.removeButton)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(VersionControlDialog)

        QMetaObject.connectSlotsByName(VersionControlDialog)

    # setupUi

    def retranslateUi(self, VersionControlDialog):
        VersionControlDialog.setWindowTitle(QCoreApplication.translate("VersionControlDialog",
                                                                       u"\u041a\u043e\u043d\u0442\u0440\u043e\u043b\u044c \u0432\u0435\u0440\u0441\u0438\u0439",
                                                                       None))
        self.label.setText(
            QCoreApplication.translate("VersionControlDialog", u"\u0412\u0435\u0440\u0441\u0438\u044f:", None))
        self.label_2.setText(
            QCoreApplication.translate("VersionControlDialog", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435:",
                                       None))
        self.saveButton.setText(QCoreApplication.translate("VersionControlDialog",
                                                           u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u0430\u043a \u0442\u0435\u043a\u0443\u0449\u0443\u044e",
                                                           None))
        self.newButton.setText(QCoreApplication.translate("VersionControlDialog",
                                                          u"\u041d\u043e\u0432\u0430\u044f \u0432\u0435\u0440\u0441\u0438\u044f",
                                                          None))
        self.removeButton.setText(
            QCoreApplication.translate("VersionControlDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
    # retranslateUi
