# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_test_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SelectTestDialog(object):
    def setupUi(self, SelectTestDialog):
        if not SelectTestDialog.objectName():
            SelectTestDialog.setObjectName(u"SelectTestDialog")
        SelectTestDialog.resize(535, 504)
        self.gridLayout_2 = QGridLayout(SelectTestDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(SelectTestDialog)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.selectButton = QPushButton(SelectTestDialog)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout.addWidget(self.selectButton)

        self.cancelButton = QPushButton(SelectTestDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(SelectTestDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(SelectTestDialog)

        QMetaObject.connectSlotsByName(SelectTestDialog)

    # setupUi

    def retranslateUi(self, SelectTestDialog):
        SelectTestDialog.setWindowTitle(QCoreApplication.translate("SelectTestDialog",
                                                                   u"\u0412\u044b\u0431\u043e\u0440 \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f",
                                                                   None))
        self.selectButton.setText(
            QCoreApplication.translate("SelectTestDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.cancelButton.setText(
            QCoreApplication.translate("SelectTestDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi
