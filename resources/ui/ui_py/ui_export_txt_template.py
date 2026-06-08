# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_txt_template.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class Ui_ExportTxtDialog(object):
    def setupUi(self, ExportTxtDialog):
        if not ExportTxtDialog.objectName():
            ExportTxtDialog.setObjectName(u"ExportTxtDialog")
        ExportTxtDialog.resize(551, 410)
        ExportTxtDialog.setMinimumSize(QSize(500, 400))
        self.verticalLayout_3 = QVBoxLayout(ExportTxtDialog)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.destinationGroupBox = QGroupBox(ExportTxtDialog)
        self.destinationGroupBox.setObjectName(u"destinationGroupBox")
        self.gridLayout = QGridLayout(self.destinationGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_4 = QLabel(self.destinationGroupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.templateName = QLineEdit(self.destinationGroupBox)
        self.templateName.setObjectName(u"templateName")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.templateName)

        self.label_3 = QLabel(self.destinationGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.exportPathLineEdit = QLineEdit(self.destinationGroupBox)
        self.exportPathLineEdit.setObjectName(u"exportPathLineEdit")
        self.exportPathLineEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.exportPathLineEdit)

        self.selectButton = QPushButton(self.destinationGroupBox)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout_2.addWidget(self.selectButton)


        self.formLayout_2.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout_2)


        self.gridLayout.addLayout(self.formLayout_2, 0, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.destinationGroupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(ExportTxtDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.loadPushButton = QPushButton(self.groupBox)
        self.loadPushButton.setObjectName(u"loadPushButton")

        self.verticalLayout.addWidget(self.loadPushButton)

        self.templatePlainText = QPlainTextEdit(self.groupBox)
        self.templatePlainText.setObjectName(u"templatePlainText")

        self.verticalLayout.addWidget(self.templatePlainText)

        self.savePushButton = QPushButton(self.groupBox)
        self.savePushButton.setObjectName(u"savePushButton")

        self.verticalLayout.addWidget(self.savePushButton)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(ExportTxtDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.searchLineEdit = QLineEdit(self.groupBox_2)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.verticalLayout_5.addWidget(self.searchLineEdit)

        self.paramListWidget = QListWidget(self.groupBox_2)
        self.paramListWidget.setObjectName(u"paramListWidget")

        self.verticalLayout_5.addWidget(self.paramListWidget)

        self.replaceButton = QPushButton(self.groupBox_2)
        self.replaceButton.setObjectName(u"replaceButton")

        self.verticalLayout_5.addWidget(self.replaceButton)


        self.gridLayout_3.addLayout(self.verticalLayout_5, 0, 0, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.buttonBox = QDialogButtonBox(ExportTxtDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_3.addWidget(self.buttonBox)


        self.retranslateUi(ExportTxtDialog)

        QMetaObject.connectSlotsByName(ExportTxtDialog)
    # setupUi

    def retranslateUi(self, ExportTxtDialog):
        ExportTxtDialog.setWindowTitle(QCoreApplication.translate("ExportTxtDialog", u"\u042d\u043a\u0441\u043f\u043e\u0440\u0442 \u043f\u043e \u0448\u0430\u0431\u043b\u043e\u043d\u0443", None))
        self.destinationGroupBox.setTitle(QCoreApplication.translate("ExportTxtDialog", u"\u0414\u0430\u043d\u043d\u044b\u0435 \u0434\u043b\u044f \u044d\u043a\u0441\u043f\u043e\u0440\u0442\u0430", None))
        self.label_4.setText(QCoreApplication.translate("ExportTxtDialog", u"\u0428\u0430\u0431\u043b\u043e\u043d \u0438\u043c\u0435\u043d\u0438 \u0444\u0430\u0439\u043b\u043e\u0432", None))
        self.label_3.setText(QCoreApplication.translate("ExportTxtDialog", u"\u041f\u0443\u0442\u044c \u044d\u043a\u0441\u043f\u043e\u0440\u0442\u0430", None))
        self.selectButton.setText(QCoreApplication.translate("ExportTxtDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c..", None))
        self.groupBox.setTitle(QCoreApplication.translate("ExportTxtDialog", u"\u0428\u0430\u0431\u043b\u043e\u043d", None))
        self.loadPushButton.setText(QCoreApplication.translate("ExportTxtDialog", u"\u0417\u0430\u0433\u0443\u0437\u0438\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d..", None))
        self.templatePlainText.setPlainText("")
        self.savePushButton.setText(QCoreApplication.translate("ExportTxtDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0448\u0430\u0431\u043b\u043e\u043d", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ExportTxtDialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b", None))
        self.replaceButton.setText(QCoreApplication.translate("ExportTxtDialog", u"\u0417\u0430\u043c\u0435\u043d\u0438\u0442\u044c", None))
    # retranslateUi

