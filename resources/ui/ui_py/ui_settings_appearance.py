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
        SettingsAppearance.resize(420, 320)
        self.gridLayout = QGridLayout(SettingsAppearance)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName(u"mainLayout")
        self.modernUiTitleLabel = QLabel(SettingsAppearance)
        self.modernUiTitleLabel.setObjectName(u"modernUiTitleLabel")
        self.modernUiTitleLabel.setStyleSheet(u"font-weight: 600;")

        self.mainLayout.addWidget(self.modernUiTitleLabel)

        self.modernUiCheckBox = QCheckBox(SettingsAppearance)
        self.modernUiCheckBox.setObjectName(u"modernUiCheckBox")

        self.mainLayout.addWidget(self.modernUiCheckBox)

        self.modernUiDescriptionLabel = QLabel(SettingsAppearance)
        self.modernUiDescriptionLabel.setObjectName(u"modernUiDescriptionLabel")
        self.modernUiDescriptionLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.modernUiDescriptionLabel)

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


        self.mainLayout.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 251, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)


        self.retranslateUi(SettingsAppearance)

        QMetaObject.connectSlotsByName(SettingsAppearance)
    # setupUi

    def retranslateUi(self, SettingsAppearance):
        SettingsAppearance.setWindowTitle(QCoreApplication.translate("SettingsAppearance", u"Form", None))
        self.modernUiTitleLabel.setText(QCoreApplication.translate("SettingsAppearance", u"\u0418\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441", None))
        self.modernUiCheckBox.setText(QCoreApplication.translate("SettingsAppearance", u"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043e\u0431\u043d\u043e\u0432\u043b\u0451\u043d\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441 (2025)", None))
        self.modernUiDescriptionLabel.setText(QCoreApplication.translate("SettingsAppearance", u"\u0421\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u0430\u044f \u0441\u0432\u0435\u0442\u043b\u0430\u044f \u0442\u0435\u043c\u0430 \u0441 \u043c\u044f\u0433\u043a\u0438\u043c\u0438 \u0446\u0432\u0435\u0442\u0430\u043c\u0438 \u0438 \u043f\u043b\u0430\u0432\u043d\u044b\u043c\u0438 \u0433\u0440\u0430\u043d\u0438\u0446\u0430\u043c\u0438.", None))
        self.customFontCheckBox.setText(QCoreApplication.translate("SettingsAppearance", u"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u0441\u0432\u043e\u0439 \u0448\u0440\u0438\u0444\u0442:", None))
        self.label.setText(QCoreApplication.translate("SettingsAppearance", u"\u0420\u0430\u0437\u043c\u0435\u0440:", None))
    # retranslateUi

