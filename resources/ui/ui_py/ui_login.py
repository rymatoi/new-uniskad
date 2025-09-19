# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from widgets.password import PasswordEdit


class Ui_UniLoginDialog(object):
    def setupUi(self, UniLoginDialog):
        if not UniLoginDialog.objectName():
            UniLoginDialog.setObjectName(u"UniLoginDialog")
        UniLoginDialog.resize(340, 259)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(UniLoginDialog.sizePolicy().hasHeightForWidth())
        UniLoginDialog.setSizePolicy(sizePolicy)
        UniLoginDialog.setMinimumSize(QSize(200, 0))
        self.verticalLayout_2 = QVBoxLayout(UniLoginDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.groupBox = QGroupBox(UniLoginDialog)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.loginLayout = QVBoxLayout()
        self.loginLayout.setObjectName(u"loginLayout")
        self.username = QLineEdit(self.groupBox)
        self.username.setObjectName(u"username")
        self.username.setMinimumSize(QSize(250, 0))

        self.loginLayout.addWidget(self.username)

        self.password = PasswordEdit(self.groupBox)
        self.password.setObjectName(u"password")
        self.password.setFocusPolicy(Qt.WheelFocus)
        self.password.setEchoMode(QLineEdit.Password)

        self.loginLayout.addWidget(self.password)

        self.verticalLayout_5.addLayout(self.loginLayout)

        self.registrationExtension = QWidget(self.groupBox)
        self.registrationExtension.setObjectName(u"registrationExtension")
        sizePolicy1.setHeightForWidth(self.registrationExtension.sizePolicy().hasHeightForWidth())
        self.registrationExtension.setSizePolicy(sizePolicy1)
        self.verticalLayout_6 = QVBoxLayout(self.registrationExtension)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_5.addWidget(self.registrationExtension)

        self.verticalLayout_2.addWidget(self.groupBox)

        self.errorBox = QLabel(UniLoginDialog)
        self.errorBox.setObjectName(u"errorBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.errorBox.sizePolicy().hasHeightForWidth())
        self.errorBox.setSizePolicy(sizePolicy2)
        self.errorBox.setStyleSheet(u"background-color: rgb(253, 155, 159);\n"
                                    "border-width: 2px;\n"
                                    "border-radius: 5px;\n"
                                    "padding: 8px;\n"
                                    "")
        self.errorBox.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.errorBox)

        self.messageBox = QLabel(UniLoginDialog)
        self.messageBox.setObjectName(u"messageBox")
        sizePolicy2.setHeightForWidth(self.messageBox.sizePolicy().hasHeightForWidth())
        self.messageBox.setSizePolicy(sizePolicy2)
        self.messageBox.setStyleSheet(u"background-color: rgb(187, 249, 187);\n"
                                      "border-width: 2px;\n"
                                      "border-radius: 5px;\n"
                                      "padding: 8px;\n"
                                      "")
        self.messageBox.setAlignment(Qt.AlignCenter)
        self.messageBox.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.messageBox)

        self.loginButton = QPushButton(UniLoginDialog)
        self.loginButton.setObjectName(u"loginButton")

        self.verticalLayout_2.addWidget(self.loginButton)

        self.verticalLayout_2.setStretch(3, 1)

        self.retranslateUi(UniLoginDialog)

        QMetaObject.connectSlotsByName(UniLoginDialog)

    # setupUi

    def retranslateUi(self, UniLoginDialog):
        UniLoginDialog.setWindowTitle(QCoreApplication.translate("UniLoginDialog",
                                                                 u"\u0410\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f",
                                                                 None))
        self.groupBox.setTitle("")
        self.username.setPlaceholderText(QCoreApplication.translate("UniLoginDialog",
                                                                    u"\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
                                                                    None))
        self.password.setPlaceholderText(
            QCoreApplication.translate("UniLoginDialog", u"\u041f\u0430\u0440\u043e\u043b\u044c", None))
        self.errorBox.setText("")
        self.messageBox.setText("")
        self.loginButton.setText(QCoreApplication.translate("UniLoginDialog", u"\u0412\u0445\u043e\u0434", None))
    # retranslateUi
