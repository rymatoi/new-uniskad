# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_plot_templates.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_EditPlotTemplatesDialog(object):
    def setupUi(self, EditPlotTemplatesDialog):
        if not EditPlotTemplatesDialog.objectName():
            EditPlotTemplatesDialog.setObjectName(u"EditPlotTemplatesDialog")
        EditPlotTemplatesDialog.resize(554, 313)
        self.gridLayout = QGridLayout(EditPlotTemplatesDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.namesTreeWidget = QTreeWidget(EditPlotTemplatesDialog)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.namesTreeWidget.setHeaderItem(__qtreewidgetitem)
        self.namesTreeWidget.setObjectName(u"namesTreeWidget")

        self.horizontalLayout.addWidget(self.namesTreeWidget)

        self.plainTextEdit = QPlainTextEdit(EditPlotTemplatesDialog)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.horizontalLayout.addWidget(self.plainTextEdit)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.choosePushButton = QPushButton(EditPlotTemplatesDialog)
        self.choosePushButton.setObjectName(u"choosePushButton")

        self.verticalLayout.addWidget(self.choosePushButton)

        self.deletePushButton = QPushButton(EditPlotTemplatesDialog)
        self.deletePushButton.setObjectName(u"deletePushButton")

        self.verticalLayout.addWidget(self.deletePushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(EditPlotTemplatesDialog)

        QMetaObject.connectSlotsByName(EditPlotTemplatesDialog)

    # setupUi

    def retranslateUi(self, EditPlotTemplatesDialog):
        EditPlotTemplatesDialog.setWindowTitle(QCoreApplication.translate("EditPlotTemplatesDialog",
                                                                          u"\u0412\u044b\u0431\u043e\u0440 \u0448\u0430\u0431\u043b\u043e\u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u043e\u0432",
                                                                          None))
        self.choosePushButton.setText(
            QCoreApplication.translate("EditPlotTemplatesDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.deletePushButton.setText(
            QCoreApplication.translate("EditPlotTemplatesDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
    # retranslateUi
