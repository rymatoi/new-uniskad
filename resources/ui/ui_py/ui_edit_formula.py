# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_formula.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_EditFormulaDialog(object):
    def setupUi(self, EditFormulaDialog):
        if not EditFormulaDialog.objectName():
            EditFormulaDialog.setObjectName(u"EditFormulaDialog")
        EditFormulaDialog.resize(560, 592)
        self.gridLayout_2 = QGridLayout(EditFormulaDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.addPushButton = QPushButton(EditFormulaDialog)
        self.addPushButton.setObjectName(u"addPushButton")

        self.verticalLayout.addWidget(self.addPushButton)

        self.editPushButton = QPushButton(EditFormulaDialog)
        self.editPushButton.setObjectName(u"editPushButton")

        self.verticalLayout.addWidget(self.editPushButton)

        self.removePushButton = QPushButton(EditFormulaDialog)
        self.removePushButton.setObjectName(u"removePushButton")

        self.verticalLayout.addWidget(self.removePushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(EditFormulaDialog)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit = QLineEdit(EditFormulaDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.treeWidget = QTreeWidget(EditFormulaDialog)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeWidget.setHeaderItem(__qtreewidgetitem)
        self.treeWidget.setObjectName(u"treeWidget")

        self.gridLayout.addWidget(self.treeWidget, 1, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.label = QLabel(EditFormulaDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.formulaLineEdit = QLineEdit(EditFormulaDialog)
        self.formulaLineEdit.setObjectName(u"formulaLineEdit")

        self.verticalLayout_2.addWidget(self.formulaLineEdit)


        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.savePushButton = QPushButton(EditFormulaDialog)
        self.savePushButton.setObjectName(u"savePushButton")

        self.horizontalLayout_3.addWidget(self.savePushButton)

        self.cancelPushButton = QPushButton(EditFormulaDialog)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout_3.addWidget(self.cancelPushButton)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)


        self.retranslateUi(EditFormulaDialog)

        QMetaObject.connectSlotsByName(EditFormulaDialog)
    # setupUi

    def retranslateUi(self, EditFormulaDialog):
        EditFormulaDialog.setWindowTitle(QCoreApplication.translate("EditFormulaDialog", u"\u0412\u044b\u0431\u043e\u0440 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u043e\u0432 \u0434\u043b\u044f \u0444\u043e\u0440\u043c\u0443\u043b\u044b", None))
        self.addPushButton.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.editPushButton.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.removePushButton.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_2.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0418\u043c\u044f", None))
        self.label.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0412\u044b\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0434\u043b\u044f \u0444\u043e\u0440\u043c\u0443\u043b\u044b", None))
        self.savePushButton.setText(QCoreApplication.translate("EditFormulaDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.cancelPushButton.setText(QCoreApplication.translate("EditFormulaDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

