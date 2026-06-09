# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'parameter_confirmation_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_ParameterConfirmationDialog(object):
    def setupUi(self, ParameterConfirmationDialog):
        if not ParameterConfirmationDialog.objectName():
            ParameterConfirmationDialog.setObjectName(u"ParameterConfirmationDialog")
        ParameterConfirmationDialog.resize(603, 392)
        self.gridLayout = QGridLayout(ParameterConfirmationDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_text = QLabel(ParameterConfirmationDialog)
        self.label_text.setObjectName(u"label_text")

        self.verticalLayout.addWidget(self.label_text)

        self.standard_radioButton = QRadioButton(ParameterConfirmationDialog)
        self.standard_radioButton.setObjectName(u"standard_radioButton")
        self.standard_radioButton.setChecked(True)

        self.verticalLayout.addWidget(self.standard_radioButton)

        self.synonym_radioButton = QRadioButton(ParameterConfirmationDialog)
        self.synonym_radioButton.setObjectName(u"synonym_radioButton")

        self.verticalLayout.addWidget(self.synonym_radioButton)

        self.groupBox = QGroupBox(ParameterConfirmationDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lineEdit = QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")

        self.verticalLayout_2.addWidget(self.lineEdit)

        self.treeView = QTreeView(self.groupBox)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout_2.addWidget(self.treeView)

        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.verticalLayout.addWidget(self.groupBox)

        self.buttonBox = QDialogButtonBox(ParameterConfirmationDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(ParameterConfirmationDialog)
        self.buttonBox.accepted.connect(ParameterConfirmationDialog.accept)
        self.buttonBox.rejected.connect(ParameterConfirmationDialog.reject)

        QMetaObject.connectSlotsByName(ParameterConfirmationDialog)

    # setupUi

    def retranslateUi(self, ParameterConfirmationDialog):
        ParameterConfirmationDialog.setWindowTitle(QCoreApplication.translate("ParameterConfirmationDialog",
                                                                              u"\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u043e\u0432",
                                                                              None))
        self.label_text.setText(QCoreApplication.translate("ParameterConfirmationDialog",
                                                           u"\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c \u043a\u0430\u043a:",
                                                           None))
        self.standard_radioButton.setText(
            QCoreApplication.translate("ParameterConfirmationDialog", u"\u042d\u0442\u0430\u043b\u043e\u043d", None))
        self.synonym_radioButton.setText(
            QCoreApplication.translate("ParameterConfirmationDialog", u"\u0421\u0438\u043d\u043e\u043d\u0438\u043c",
                                       None))
        self.groupBox.setTitle(QCoreApplication.translate("ParameterConfirmationDialog",
                                                          u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u044d\u0442\u0430\u043b\u043e\u043d",
                                                          None))
    # retranslateUi
