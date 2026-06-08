# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'link_eizm_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_LinkEizmDialog(object):
    def setupUi(self, LinkEizmDialog):
        if not LinkEizmDialog.objectName():
            LinkEizmDialog.setObjectName(u"LinkEizmDialog")
        LinkEizmDialog.resize(603, 392)
        self.gridLayout = QGridLayout(LinkEizmDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(LinkEizmDialog)
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

        self.buttonBox = QDialogButtonBox(LinkEizmDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(LinkEizmDialog)
        self.buttonBox.accepted.connect(LinkEizmDialog.accept)
        self.buttonBox.rejected.connect(LinkEizmDialog.reject)

        QMetaObject.connectSlotsByName(LinkEizmDialog)

    # setupUi

    def retranslateUi(self, LinkEizmDialog):
        LinkEizmDialog.setWindowTitle(QCoreApplication.translate("LinkEizmDialog",
                                                                 u"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0435\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f",
                                                                 None))
        self.groupBox.setTitle(QCoreApplication.translate("LinkEizmDialog",
                                                          u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0435\u0434\u0438\u043d\u0438\u0446\u0443 \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f",
                                                          None))
    # retranslateUi
