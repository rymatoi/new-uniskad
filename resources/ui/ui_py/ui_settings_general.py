# -*- coding: utf-8 -*-

################################################################################
## Form generated manually to provide a lightweight settings page layout
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SettingsGeneral(object):
    def setupUi(self, SettingsGeneral):
        if not SettingsGeneral.objectName():
            SettingsGeneral.setObjectName(u"SettingsGeneral")
        SettingsGeneral.resize(400, 220)
        self.verticalLayout = QVBoxLayout(SettingsGeneral)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(12)
        self.formLayout.setVerticalSpacing(8)

        self.sessionTimeoutLabel = QLabel(SettingsGeneral)
        self.sessionTimeoutLabel.setObjectName(u"sessionTimeoutLabel")
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.sessionTimeoutLabel)

        self.sessionTimeoutSpinBox = QSpinBox(SettingsGeneral)
        self.sessionTimeoutSpinBox.setObjectName(u"sessionTimeoutSpinBox")
        self.sessionTimeoutSpinBox.setRange(0, 240)
        self.sessionTimeoutSpinBox.setSpecialValueText(QCoreApplication.translate(
            "SettingsGeneral", u"\u041d\u0435 \u043e\u0442\u043a\u043b\u044e\u0447\u0430\u0442\u044c", None))
        self.sessionTimeoutSpinBox.setValue(30)
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.sessionTimeoutSpinBox)

        self.notificationTimeoutLabel = QLabel(SettingsGeneral)
        self.notificationTimeoutLabel.setObjectName(u"notificationTimeoutLabel")
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.notificationTimeoutLabel)

        self.notificationTimeoutSpinBox = QSpinBox(SettingsGeneral)
        self.notificationTimeoutSpinBox.setObjectName(u"notificationTimeoutSpinBox")
        self.notificationTimeoutSpinBox.setRange(3, 120)
        self.notificationTimeoutSpinBox.setValue(10)
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.notificationTimeoutSpinBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

        self.retranslateUi(SettingsGeneral)
        QMetaObject.connectSlotsByName(SettingsGeneral)

    def retranslateUi(self, SettingsGeneral):
        SettingsGeneral.setWindowTitle(QCoreApplication.translate("SettingsGeneral", u"General Settings", None))
        self.sessionTimeoutLabel.setText(QCoreApplication.translate(
            "SettingsGeneral", u"\u0412\u0440\u0435\u043c\u044f \u0431\u0435\u0437\u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u0434\u043e \u0430\u0432\u0442\u043e\u0432\u044b\u0445\u043e\u0434\u0430, \u043c\u0438\u043d:", None))
        self.notificationTimeoutLabel.setText(QCoreApplication.translate(
            "SettingsGeneral", u"\u0414\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f, \u0441:", None))
