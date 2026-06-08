# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_user_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_SelectUserDialog(object):
    def setupUi(self, SelectUserDialog):
        if not SelectUserDialog.objectName():
            SelectUserDialog.setObjectName(u"SelectUserDialog")
        SelectUserDialog.resize(375, 479)
        self.gridLayout_2 = QGridLayout(SelectUserDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(SelectUserDialog)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.selectButton = QPushButton(SelectUserDialog)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout.addWidget(self.selectButton)

        self.cancelButton = QPushButton(SelectUserDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(SelectUserDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(SelectUserDialog)

        QMetaObject.connectSlotsByName(SelectUserDialog)

    # setupUi

    def retranslateUi(self, SelectUserDialog):
        SelectUserDialog.setWindowTitle(QCoreApplication.translate("SelectUserDialog",
                                                                   u"\u0412\u044b\u0431\u043e\u0440 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
                                                                   None))
        self.selectButton.setText(
            QCoreApplication.translate("SelectUserDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.cancelButton.setText(
            QCoreApplication.translate("SelectUserDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
