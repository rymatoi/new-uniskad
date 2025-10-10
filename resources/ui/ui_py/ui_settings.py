# -*- coding: utf-8 -*-

################################################################################
## Form generated manually to mirror UI definition in 'settings.ui'
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(605, 466)
        self.verticalLayout = QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(SettingsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setCurrentIndex(0)
        self.generalTab = QWidget()
        self.generalTab.setObjectName(u"generalTab")
        self.generalLayout = QVBoxLayout(self.generalTab)
        self.generalLayout.setObjectName(u"generalLayout")
        self.startMaximizedCheckBox = QCheckBox(self.generalTab)
        self.startMaximizedCheckBox.setObjectName(u"startMaximizedCheckBox")
        self.generalLayout.addWidget(self.startMaximizedCheckBox)
        self.rememberGeometryCheckBox = QCheckBox(self.generalTab)
        self.rememberGeometryCheckBox.setObjectName(u"rememberGeometryCheckBox")
        self.generalLayout.addWidget(self.rememberGeometryCheckBox)
        self.showStatusBarCheckBox = QCheckBox(self.generalTab)
        self.showStatusBarCheckBox.setObjectName(u"showStatusBarCheckBox")
        self.generalLayout.addWidget(self.showStatusBarCheckBox)
        self.confirmOnExitCheckBox = QCheckBox(self.generalTab)
        self.confirmOnExitCheckBox.setObjectName(u"confirmOnExitCheckBox")
        self.generalLayout.addWidget(self.confirmOnExitCheckBox)
        self.generalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.generalLayout.addItem(self.generalSpacer)
        self.tabWidget.addTab(self.generalTab, "")
        self.appearanceTab = QWidget()
        self.appearanceTab.setObjectName(u"appearanceTab")
        self.appearanceLayout = QVBoxLayout(self.appearanceTab)
        self.appearanceLayout.setObjectName(u"appearanceLayout")
        self.customFontCheckBox = QCheckBox(self.appearanceTab)
        self.customFontCheckBox.setObjectName(u"customFontCheckBox")
        self.appearanceLayout.addWidget(self.customFontCheckBox)
        self.fontFormLayout = QFormLayout()
        self.fontFormLayout.setObjectName(u"fontFormLayout")
        self.fontFormLayout.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.fontLabel = QLabel(self.appearanceTab)
        self.fontLabel.setObjectName(u"fontLabel")
        self.fontFormLayout.setWidget(0, QFormLayout.LabelRole, self.fontLabel)
        self.fontComboBox = QFontComboBox(self.appearanceTab)
        self.fontComboBox.setObjectName(u"fontComboBox")
        self.fontFormLayout.setWidget(0, QFormLayout.FieldRole, self.fontComboBox)
        self.fontSizeLabel = QLabel(self.appearanceTab)
        self.fontSizeLabel.setObjectName(u"fontSizeLabel")
        self.fontFormLayout.setWidget(1, QFormLayout.LabelRole, self.fontSizeLabel)
        self.fontSizeSpinBox = QSpinBox(self.appearanceTab)
        self.fontSizeSpinBox.setObjectName(u"fontSizeSpinBox")
        self.fontSizeSpinBox.setMinimum(8)
        self.fontSizeSpinBox.setMaximum(48)
        self.fontSizeSpinBox.setValue(12)
        self.fontFormLayout.setWidget(1, QFormLayout.FieldRole, self.fontSizeSpinBox)
        self.themeLabel = QLabel(self.appearanceTab)
        self.themeLabel.setObjectName(u"themeLabel")
        self.fontFormLayout.setWidget(2, QFormLayout.LabelRole, self.themeLabel)
        self.themeComboBox = QComboBox(self.appearanceTab)
        self.themeComboBox.setObjectName(u"themeComboBox")
        self.fontFormLayout.setWidget(2, QFormLayout.FieldRole, self.themeComboBox)
        self.appearanceLayout.addLayout(self.fontFormLayout)
        self.appearanceSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.appearanceLayout.addItem(self.appearanceSpacer)
        self.tabWidget.addTab(self.appearanceTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalGroupBox = QGroupBox(SettingsDialog)
        self.horizontalGroupBox.setObjectName(u"horizontalGroupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalGroupBox.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBox.setSizePolicy(sizePolicy)
        self.horizontalGroupBox.setMinimumSize(QSize(0, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalGroupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
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
        self.verticalLayout.addWidget(self.horizontalGroupBox)

        self.retranslateUi(SettingsDialog)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(SettingsDialog)

    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Dialog", None))
        self.startMaximizedCheckBox.setText(
            QCoreApplication.translate("SettingsDialog", u"\u0417\u0430\u043f\u0443\u0441\u043a\u0430\u0442\u044c \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0432 \u043f\u043e\u043b\u043d\u043e\u044d\u043a\u0440\u0430\u043d\u043d\u043e\u043c \u0440\u0435\u0436\u0438\u043c\u0435", None))
        self.rememberGeometryCheckBox.setText(
            QCoreApplication.translate("SettingsDialog", u"\u0417\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u0442\u044c \u0440\u0430\u0437\u043c\u0435\u0440 \u0438 \u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043e\u043a\u043d\u0430", None))
        self.showStatusBarCheckBox.setText(
            QCoreApplication.translate("SettingsDialog", u"\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u0441\u0442\u0440\u043e\u043a\u0443 \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f", None))
        self.confirmOnExitCheckBox.setText(
            QCoreApplication.translate("SettingsDialog", u"\u0417\u0430\u043f\u0440\u0430\u0448\u0438\u0432\u0430\u0442\u044c \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u043f\u0440\u0438 \u0432\u044b\u0445\u043e\u0434\u0435", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.generalTab),
                                  QCoreApplication.translate("SettingsDialog", u"\u041e\u0431\u0449\u0438\u0435", None))
        self.customFontCheckBox.setText(
            QCoreApplication.translate("SettingsDialog", u"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u0441\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442", None))
        self.fontLabel.setText(QCoreApplication.translate("SettingsDialog", u"\u0428\u0440\u0438\u0444\u0442:", None))
        self.fontSizeLabel.setText(QCoreApplication.translate("SettingsDialog", u"\u0420\u0430\u0437\u043c\u0435\u0440:", None))
        self.themeLabel.setText(QCoreApplication.translate("SettingsDialog", u"\u0422\u0435\u043c\u0430 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441\u0430:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.appearanceTab),
                                  QCoreApplication.translate("SettingsDialog", u"\u0412\u043d\u0435\u0448\u043d\u0438\u0439 \u0432\u0438\u0434", None))
        self.acceptPushButton.setText(QCoreApplication.translate("SettingsDialog", u"\u041e\u043a", None))
        self.cancelPushButton.setText(QCoreApplication.translate("SettingsDialog", u"\u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.applyPushButton.setText(QCoreApplication.translate("SettingsDialog", u"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi
