# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'parameter_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ParameterWidget(object):
    def setupUi(self, ParameterWidget):
        if not ParameterWidget.objectName():
            ParameterWidget.setObjectName(u"ParameterWidget")
        ParameterWidget.resize(460, 411)
        self.gridLayout_2 = QGridLayout(ParameterWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(ParameterWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.checkBox = QCheckBox(ParameterWidget)
        self.checkBox.setObjectName(u"checkBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.checkBox)


        self.verticalLayout_2.addLayout(self.formLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.label = QLabel(ParameterWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.addButton = QPushButton(ParameterWidget)
        self.addButton.setObjectName(u"addButton")

        self.verticalLayout.addWidget(self.addButton)

        self.selectButton = QPushButton(ParameterWidget)
        self.selectButton.setObjectName(u"selectButton")

        self.verticalLayout.addWidget(self.selectButton)

        self.removeButton = QPushButton(ParameterWidget)
        self.removeButton.setObjectName(u"removeButton")

        self.verticalLayout.addWidget(self.removeButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)

        self.treeView = QTreeView(ParameterWidget)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)


        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(ParameterWidget)

        QMetaObject.connectSlotsByName(ParameterWidget)
    # setupUi

    def retranslateUi(self, ParameterWidget):
        ParameterWidget.setWindowTitle(QCoreApplication.translate("ParameterWidget", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("ParameterWidget", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u043e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u043d\u043e\u0439 \u0432\u0438\u0434\u0438\u043c\u043e\u0441\u0442\u0438", None))
        self.checkBox.setText("")
        self.label.setText(QCoreApplication.translate("ParameterWidget", u"\u0415\u0434\u0438\u043d\u0438\u0446\u044b \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u044f", None))
        self.addButton.setText(QCoreApplication.translate("ParameterWidget", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.selectButton.setText(QCoreApplication.translate("ParameterWidget", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.removeButton.setText(QCoreApplication.translate("ParameterWidget", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
    # retranslateUi

