# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_test_params_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SelectTestParamsDialog(object):
    def setupUi(self, SelectTestParamsDialog):
        if not SelectTestParamsDialog.objectName():
            SelectTestParamsDialog.setObjectName(u"SelectTestParamsDialog")
        SelectTestParamsDialog.resize(535, 504)
        self.gridLayout_2 = QGridLayout(SelectTestParamsDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(SelectTestParamsDialog)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout.addWidget(self.treeView, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.selectAllButton = QPushButton(SelectTestParamsDialog)
        self.selectAllButton.setObjectName(u"selectAllButton")

        self.horizontalLayout.addWidget(self.selectAllButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.selectButton = QPushButton(SelectTestParamsDialog)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout.addWidget(self.selectButton)

        self.cancelButton = QPushButton(SelectTestParamsDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)

        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.lineEdit = QLineEdit(SelectTestParamsDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(SelectTestParamsDialog)

        QMetaObject.connectSlotsByName(SelectTestParamsDialog)

    # setupUi

    def retranslateUi(self, SelectTestParamsDialog):
        SelectTestParamsDialog.setWindowTitle(QCoreApplication.translate("SelectTestParamsDialog",
                                                                         u"\u0412\u044b\u0431\u043e\u0440 \u0434\u0430\u043d\u043d\u044b\u0445",
                                                                         None))
        self.selectAllButton.setText(QCoreApplication.translate("SelectTestParamsDialog",
                                                                u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435",
                                                                None))
        self.selectButton.setText(
            QCoreApplication.translate("SelectTestParamsDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.cancelButton.setText(
            QCoreApplication.translate("SelectTestParamsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
        self.lineEdit.setInputMask("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("SelectTestParamsDialog",
                                                                    u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440..",
                                                                    None))
    # retranslateUi
