# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_eizm.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_CreateEizmDialog(object):
    def setupUi(self, CreateEizmDialog):
        if not CreateEizmDialog.objectName():
            CreateEizmDialog.setObjectName(u"CreateEizmDialog")
        CreateEizmDialog.resize(514, 296)
        self.gridLayout = QGridLayout(CreateEizmDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.nameLabel = QLabel(CreateEizmDialog)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.nameLabel)

        self.shortnameLabel = QLabel(CreateEizmDialog)
        self.shortnameLabel.setObjectName(u"shortnameLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.shortnameLabel)

        self.descriptionLabel = QLabel(CreateEizmDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.lineEdit = QLineEdit(CreateEizmDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit)

        self.lineEdit_2 = QLineEdit(CreateEizmDialog)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_2)

        self.plainTextEdit = QPlainTextEdit(CreateEizmDialog)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.plainTextEdit)

        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(CreateEizmDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(CreateEizmDialog)
        self.buttonBox.accepted.connect(CreateEizmDialog.accept)
        self.buttonBox.rejected.connect(CreateEizmDialog.reject)

        QMetaObject.connectSlotsByName(CreateEizmDialog)

    # setupUi

    def retranslateUi(self, CreateEizmDialog):
        CreateEizmDialog.setWindowTitle(QCoreApplication.translate("CreateEizmDialog",
                                                                   u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0435\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f",
                                                                   None))
        self.nameLabel.setText(
            QCoreApplication.translate("CreateEizmDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.shortnameLabel.setText(QCoreApplication.translate("CreateEizmDialog",
                                                               u"\u0421\u043e\u043a\u0440\u0430\u0449\u0435\u043d\u0438\u0435:",
                                                               None))
        self.descriptionLabel.setText(
            QCoreApplication.translate("CreateEizmDialog", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435:", None))
    # retranslateUi
