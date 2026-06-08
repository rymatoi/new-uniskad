# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_config.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_CreateConfigDialog(object):
    def setupUi(self, CreateConfigDialog):
        if not CreateConfigDialog.objectName():
            CreateConfigDialog.setObjectName(u"CreateConfigDialog")
        CreateConfigDialog.resize(432, 373)
        self.gridLayout_4 = QGridLayout(CreateConfigDialog)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.createPushButton = QPushButton(CreateConfigDialog)
        self.createPushButton.setObjectName(u"createPushButton")

        self.gridLayout.addWidget(self.createPushButton, 2, 0, 1, 1)

        self.groupBox = QGroupBox(CreateConfigDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.hostLineEdit = QLineEdit(self.groupBox)
        self.hostLineEdit.setObjectName(u"hostLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.hostLineEdit)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.portLineEdit = QLineEdit(self.groupBox)
        self.portLineEdit.setObjectName(u"portLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.portLineEdit)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.usernameLineEdit = QLineEdit(self.groupBox)
        self.usernameLineEdit.setObjectName(u"usernameLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.usernameLineEdit)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.passwordLineEdit = QLineEdit(self.groupBox)
        self.passwordLineEdit.setObjectName(u"passwordLineEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.passwordLineEdit)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.databaseLineEdit = QLineEdit(self.groupBox)
        self.databaseLineEdit.setObjectName(u"databaseLineEdit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.databaseLineEdit)

        self.gridLayout_2.addLayout(self.formLayout, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(CreateConfigDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setEnabled(False)
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_6)

        self.hostLineEdit_2 = QLineEdit(self.groupBox_2)
        self.hostLineEdit_2.setObjectName(u"hostLineEdit_2")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.hostLineEdit_2)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_7)

        self.portLineEdit_2 = QLineEdit(self.groupBox_2)
        self.portLineEdit_2.setObjectName(u"portLineEdit_2")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.portLineEdit_2)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_8)

        self.usernameLineEdit_2 = QLineEdit(self.groupBox_2)
        self.usernameLineEdit_2.setObjectName(u"usernameLineEdit_2")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.usernameLineEdit_2)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_9)

        self.passwordLineEdit_2 = QLineEdit(self.groupBox_2)
        self.passwordLineEdit_2.setObjectName(u"passwordLineEdit_2")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.passwordLineEdit_2)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_10)

        self.databaseLineEdit_2 = QLineEdit(self.groupBox_2)
        self.databaseLineEdit_2.setObjectName(u"databaseLineEdit_2")

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.databaseLineEdit_2)

        self.gridLayout_3.addLayout(self.formLayout_2, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(CreateConfigDialog)

        QMetaObject.connectSlotsByName(CreateConfigDialog)

    # setupUi

    def retranslateUi(self, CreateConfigDialog):
        CreateConfigDialog.setWindowTitle(QCoreApplication.translate("CreateConfigDialog",
                                                                     u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043d\u043e\u0432\u043e\u0433\u043e \u043a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u043e\u043d\u043d\u043e\u0433\u043e \u0444\u0430\u0439\u043b\u0430",
                                                                     None))
        self.createPushButton.setText(
            QCoreApplication.translate("CreateConfigDialog", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c", None))
        self.groupBox.setTitle(QCoreApplication.translate("CreateConfigDialog",
                                                          u"\u0423\u0434\u0430\u043b\u0435\u043d\u043d\u0430\u044f \u0411\u0414",
                                                          None))
        self.label.setText(QCoreApplication.translate("CreateConfigDialog", u"\u0425\u043e\u0441\u0442:", None))
        self.label_2.setText(QCoreApplication.translate("CreateConfigDialog", u"\u041f\u043e\u0440\u0442:", None))
        self.label_3.setText(QCoreApplication.translate("CreateConfigDialog",
                                                        u"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c:",
                                                        None))
        self.label_4.setText(
            QCoreApplication.translate("CreateConfigDialog", u"\u041f\u0430\u0440\u043e\u043b\u044c:", None))
        self.label_5.setText(QCoreApplication.translate("CreateConfigDialog",
                                                        u"\u0411\u0430\u0437\u0430 \u0434\u0430\u043d\u043d\u044b\u0445:",
                                                        None))
        self.groupBox_2.setTitle(QCoreApplication.translate("CreateConfigDialog",
                                                            u"\u041b\u043e\u043a\u0430\u043b\u044c\u043d\u0430\u044f \u0411\u0414",
                                                            None))
        self.label_6.setText(QCoreApplication.translate("CreateConfigDialog", u"\u0425\u043e\u0441\u0442:", None))
        self.label_7.setText(QCoreApplication.translate("CreateConfigDialog", u"\u041f\u043e\u0440\u0442:", None))
        self.label_8.setText(QCoreApplication.translate("CreateConfigDialog",
                                                        u"\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c:",
                                                        None))
        self.label_9.setText(
            QCoreApplication.translate("CreateConfigDialog", u"\u041f\u0430\u0440\u043e\u043b\u044c:", None))
        self.label_10.setText(QCoreApplication.translate("CreateConfigDialog",
                                                         u"\u0411\u0430\u0437\u0430 \u0434\u0430\u043d\u043d\u044b\u0445:",
                                                         None))
    # retranslateUi
