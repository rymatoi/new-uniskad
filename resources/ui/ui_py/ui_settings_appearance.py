# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_appearance.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SettingsAppearance(object):
    def setupUi(self, SettingsAppearance):
        if not SettingsAppearance.objectName():
            SettingsAppearance.setObjectName(u"SettingsAppearance")
        SettingsAppearance.resize(400, 300)
        self.gridLayout = QGridLayout(SettingsAppearance)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.customFontCheckBox = QCheckBox(SettingsAppearance)
        self.customFontCheckBox.setObjectName(u"customFontCheckBox")

        self.horizontalLayout.addWidget(self.customFontCheckBox)

        self.fontComboBox = QComboBox(SettingsAppearance)
        self.fontComboBox.setObjectName(u"fontComboBox")

        self.horizontalLayout.addWidget(self.fontComboBox)

        self.label = QLabel(SettingsAppearance)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.fontSizeComboBox = QComboBox(SettingsAppearance)
        self.fontSizeComboBox.setObjectName(u"fontSizeComboBox")

        self.horizontalLayout.addWidget(self.fontSizeComboBox)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.modernUiButton = QPushButton(SettingsAppearance)
        self.modernUiButton.setObjectName(u"modernUiButton")
        self.modernUiButton.setCheckable(True)
        self.modernUiButton.setMinimumHeight(36)

        self.gridLayout.addWidget(self.modernUiButton, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 211, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.retranslateUi(SettingsAppearance)

        QMetaObject.connectSlotsByName(SettingsAppearance)

    # setupUi

    def retranslateUi(self, SettingsAppearance):
        SettingsAppearance.setWindowTitle(QCoreApplication.translate("SettingsAppearance", u"Form", None))
        self.customFontCheckBox.setText(QCoreApplication.translate("SettingsAppearance",
                                                                   u"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u0441\u0432\u043e\u0439 \u0448\u0440\u0438\u0444\u0442:",
                                                                   None))
        self.label.setText(
            QCoreApplication.translate("SettingsAppearance", u"\u0420\u0430\u0437\u043c\u0435\u0440:", None))
        self.modernUiButton.setText(
            QCoreApplication.translate("SettingsAppearance", u"\u0418\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441 2025: \u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d", None))
    # retranslateUi
