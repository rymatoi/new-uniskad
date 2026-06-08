# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(605, 466)
        self.gridLayout_2 = QGridLayout(SettingsDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.splitter = QSplitter(SettingsDialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName(u"treeView")
        self.splitter.addWidget(self.treeView)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.splitter.addWidget(self.widget)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.horizontalGroupBox = QGroupBox(SettingsDialog)
        self.horizontalGroupBox.setObjectName(u"horizontalGroupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalGroupBox.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBox.setSizePolicy(sizePolicy)
        self.horizontalGroupBox.setMinimumSize(QSize(0, 41))
        self.horizontalGroupBox.setMaximumHeight(50)
        self.horizontalLayout = QHBoxLayout(self.horizontalGroupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.acceptPushButton = QPushButton(self.horizontalGroupBox)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout.addWidget(self.acceptPushButton)

        self.cancelPushButton = QPushButton(self.horizontalGroupBox)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self.horizontalGroupBox)
        self.applyPushButton.setObjectName(u"applyPushButton")

        self.horizontalLayout.addWidget(self.applyPushButton)

        self.gridLayout.addWidget(self.horizontalGroupBox, 1, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)

    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Dialog", None))
        self.acceptPushButton.setText(QCoreApplication.translate("SettingsDialog", u"\u041e\u043a", None))
        self.cancelPushButton.setText(
            QCoreApplication.translate("SettingsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.applyPushButton.setText(
            QCoreApplication.translate("SettingsDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c",
                                       None))
    # retranslateUi
