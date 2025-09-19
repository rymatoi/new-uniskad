# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'link_role_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_LinkRoleDialog(object):
    def setupUi(self, LinkRoleDialog):
        if not LinkRoleDialog.objectName():
            LinkRoleDialog.setObjectName(u"LinkRoleDialog")
        LinkRoleDialog.resize(603, 392)
        self.gridLayout = QGridLayout(LinkRoleDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(LinkRoleDialog)
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

        self.buttonBox = QDialogButtonBox(LinkRoleDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(LinkRoleDialog)
        self.buttonBox.accepted.connect(LinkRoleDialog.accept)
        self.buttonBox.rejected.connect(LinkRoleDialog.reject)

        QMetaObject.connectSlotsByName(LinkRoleDialog)

    # setupUi

    def retranslateUi(self, LinkRoleDialog):
        LinkRoleDialog.setWindowTitle(QCoreApplication.translate("LinkRoleDialog",
                                                                 u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0440\u043e\u043b\u0438",
                                                                 None))
        self.groupBox.setTitle(QCoreApplication.translate("LinkRoleDialog",
                                                          u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0440\u043e\u043b\u044c",
                                                          None))
    # retranslateUi
