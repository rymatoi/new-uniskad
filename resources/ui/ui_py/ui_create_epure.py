# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_epure.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_CreateEpureDialog(object):
    def setupUi(self, CreateEpureDialog):
        if not CreateEpureDialog.objectName():
            CreateEpureDialog.setObjectName(u"CreateEpureDialog")
        CreateEpureDialog.resize(613, 496)
        self.gridLayout = QGridLayout(CreateEpureDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(CreateEpureDialog)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_5.addWidget(self.label_4)

        self.nameLineEdit = QLineEdit(CreateEpureDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.horizontalLayout_5.addWidget(self.nameLineEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(CreateEpureDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.paramsTreeView = QTreeView(CreateEpureDialog)
        self.paramsTreeView.setObjectName(u"paramsTreeView")

        self.verticalLayout.addWidget(self.paramsTreeView)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.addParamPushButton = QPushButton(CreateEpureDialog)
        self.addParamPushButton.setObjectName(u"addParamPushButton")

        self.verticalLayout_2.addWidget(self.addParamPushButton)

        self.removeParamPushButton = QPushButton(CreateEpureDialog)
        self.removeParamPushButton.setObjectName(u"removeParamPushButton")

        self.verticalLayout_2.addWidget(self.removeParamPushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(CreateEpureDialog)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.selectParam = QPushButton(CreateEpureDialog)
        self.selectParam.setObjectName(u"selectParam")

        self.horizontalLayout_3.addWidget(self.selectParam)

        self.paramValuesLineEdit = QLineEdit(CreateEpureDialog)
        self.paramValuesLineEdit.setObjectName(u"paramValuesLineEdit")

        self.horizontalLayout_3.addWidget(self.paramValuesLineEdit)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout_3.addLayout(self.verticalLayout_4)

        self.oySetupPushButton = QPushButton(CreateEpureDialog)
        self.oySetupPushButton.setObjectName(u"oySetupPushButton")

        self.verticalLayout_3.addWidget(self.oySetupPushButton)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.acceptPushButton = QPushButton(CreateEpureDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout_2.addWidget(self.acceptPushButton)

        self.cancelPushButton = QPushButton(CreateEpureDialog)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout_2.addWidget(self.cancelPushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(CreateEpureDialog)

        QMetaObject.connectSlotsByName(CreateEpureDialog)
    # setupUi

    def retranslateUi(self, CreateEpureDialog):
        CreateEpureDialog.setWindowTitle(QCoreApplication.translate("CreateEpureDialog", u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u0435\u0439", None))
        self.label_4.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.label.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u043e\u0441\u044c X", None))
        self.addParamPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c ..", None))
        self.removeParamPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_2.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440", None))
        self.selectParam.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440", None))
        self.oySetupPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0441\u0438 OY", None))
        self.acceptPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041e\u043a", None))
        self.cancelPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

