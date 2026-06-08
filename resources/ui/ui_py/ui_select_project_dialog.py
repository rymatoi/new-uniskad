# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_project_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_SelectProjectDialog(object):
    def setupUi(self, SelectProjectDialog):
        if not SelectProjectDialog.objectName():
            SelectProjectDialog.setObjectName(u"SelectProjectDialog")
        SelectProjectDialog.resize(837, 841)
        self.gridLayout_4 = QGridLayout(SelectProjectDialog)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_2 = QGroupBox(SelectProjectDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.othersProjectsTreeWidget = QTreeWidget(self.groupBox_2)
        self.othersProjectsTreeWidget.setObjectName(u"othersProjectsTreeWidget")

        self.gridLayout_3.addWidget(self.othersProjectsTreeWidget, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 1)

        self.groupBox = QGroupBox(SelectProjectDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.ownProjectsTreeWidget = QTreeWidget(self.groupBox)
        self.ownProjectsTreeWidget.setObjectName(u"ownProjectsTreeWidget")

        self.gridLayout_2.addWidget(self.ownProjectsTreeWidget, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lineEdit = QLineEdit(SelectProjectDialog)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_3.addWidget(self.lineEdit)

        self.settingsButton = QPushButton(SelectProjectDialog)
        self.settingsButton.setObjectName(u"settingsButton")

        self.horizontalLayout_3.addWidget(self.settingsButton)


        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.createButton = QPushButton(SelectProjectDialog)
        self.createButton.setObjectName(u"createButton")

        self.verticalLayout.addWidget(self.createButton)

        self.renameButton = QPushButton(SelectProjectDialog)
        self.renameButton.setObjectName(u"renameButton")

        self.verticalLayout.addWidget(self.renameButton)

        self.copyButton = QPushButton(SelectProjectDialog)
        self.copyButton.setObjectName(u"copyButton")

        self.verticalLayout.addWidget(self.copyButton)

        self.passProjectButton = QPushButton(SelectProjectDialog)
        self.passProjectButton.setObjectName(u"passProjectButton")

        self.verticalLayout.addWidget(self.passProjectButton)

        self.removeButton = QPushButton(SelectProjectDialog)
        self.removeButton.setObjectName(u"removeButton")

        self.verticalLayout.addWidget(self.removeButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.selectButton = QPushButton(SelectProjectDialog)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout.addWidget(self.selectButton)

        self.cancelButton = QPushButton(SelectProjectDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(SelectProjectDialog)

        QMetaObject.connectSlotsByName(SelectProjectDialog)
    # setupUi

    def retranslateUi(self, SelectProjectDialog):
        SelectProjectDialog.setWindowTitle(QCoreApplication.translate("SelectProjectDialog", u"\u0412\u044b\u0431\u043e\u0440 \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SelectProjectDialog", u"\u041f\u0440\u043e\u0435\u043a\u0442\u044b \u0434\u0440\u0443\u0433\u0438\u0445 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439", None))
        ___qtreewidgetitem = self.othersProjectsTreeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("SelectProjectDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None));
        self.groupBox.setTitle(QCoreApplication.translate("SelectProjectDialog", u"\u041b\u0438\u0447\u043d\u044b\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u044b", None))
        ___qtreewidgetitem1 = self.ownProjectsTreeWidget.headerItem()
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("SelectProjectDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None));
        self.settingsButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u041f\u0435\u0440\u0435\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043d\u0430 \u043f\u043e\u0438\u0441\u043a \u043f\u043e \u0434\u0430\u0442\u0435", None))
        self.createButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c..", None))
        self.renameButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u041f\u0435\u0440\u0435\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u0442\u044c..", None))
        self.copyButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043a\u043e\u043f\u0438\u044e", None))
        self.passProjectButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043a\u043e\u043f\u0438\u044e ..", None))
        self.removeButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.selectButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u041e\u0442\u043a\u0440\u044b\u0442\u044c", None))
        self.cancelButton.setText(QCoreApplication.translate("SelectProjectDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

