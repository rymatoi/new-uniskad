# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'row_settings.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_RowSettingsDialog(object):
    def setupUi(self, RowSettingsDialog):
        if not RowSettingsDialog.objectName():
            RowSettingsDialog.setObjectName(u"RowSettingsDialog")
        RowSettingsDialog.resize(327, 186)
        self.gridLayout_2 = QGridLayout(RowSettingsDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_2 = QLabel(RowSettingsDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.nameLineEdit = QLineEdit(RowSettingsDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.label = QLabel(RowSettingsDialog)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.accuracySpinBox = QSpinBox(RowSettingsDialog)
        self.accuracySpinBox.setObjectName(u"accuracySpinBox")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.accuracySpinBox)

        self.verticalLayout.addLayout(self.formLayout_2)

        self.groupBox = QGroupBox(RowSettingsDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout_4 = QFormLayout()
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.fromComboBox_2 = QComboBox(self.groupBox)
        self.fromComboBox_2.setObjectName(u"fromComboBox_2")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fromComboBox_2)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.toComboBox_2 = QComboBox(self.groupBox)
        self.toComboBox_2.setObjectName(u"toComboBox_2")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.toComboBox_2)

        self.gridLayout.addLayout(self.formLayout_4, 0, 0, 1, 1)

        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.savePushButton = QPushButton(RowSettingsDialog)
        self.savePushButton.setObjectName(u"savePushButton")

        self.horizontalLayout.addWidget(self.savePushButton)

        self.cancelButton = QPushButton(RowSettingsDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(RowSettingsDialog)

        QMetaObject.connectSlotsByName(RowSettingsDialog)

    # setupUi

    def retranslateUi(self, RowSettingsDialog):
        RowSettingsDialog.setWindowTitle(QCoreApplication.translate("RowSettingsDialog",
                                                                    u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u0438",
                                                                    None))
        self.label_2.setText(
            QCoreApplication.translate("RowSettingsDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.label.setText(QCoreApplication.translate("RowSettingsDialog",
                                                      u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0437\u043d\u0430\u0447\u0430\u0449\u0438\u0445 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432:",
                                                      None))
        self.groupBox.setTitle(QCoreApplication.translate("RowSettingsDialog",
                                                          u"\u041f\u0435\u0440\u0435\u0441\u0447\u0435\u0442 \u0435\u0434\u0438\u043d\u0438\u0446 \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f",
                                                          None))
        self.label_5.setText(QCoreApplication.translate("RowSettingsDialog", u"\u0418\u0437:", None))
        self.label_6.setText(QCoreApplication.translate("RowSettingsDialog", u"\u0412:", None))
        self.savePushButton.setText(
            QCoreApplication.translate("RowSettingsDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",
                                       None))
        self.cancelButton.setText(
            QCoreApplication.translate("RowSettingsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
