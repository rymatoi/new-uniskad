# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'manage_user_formulas.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ListTemplateFormulas(object):
    def setupUi(self, ListTemplateFormulas):
        if not ListTemplateFormulas.objectName():
            ListTemplateFormulas.setObjectName(u"ListTemplateFormulas")
        ListTemplateFormulas.resize(664, 597)
        self.gridLayout_2 = QGridLayout(ListTemplateFormulas)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.addParamsPushButton = QPushButton(ListTemplateFormulas)
        self.addParamsPushButton.setObjectName(u"addParamsPushButton")

        self.horizontalLayout_2.addWidget(self.addParamsPushButton)

        self.helpToolButton = QToolButton(ListTemplateFormulas)
        self.helpToolButton.setObjectName(u"helpToolButton")
        self.helpToolButton.setAutoRaise(True)

        self.horizontalLayout_2.addWidget(self.helpToolButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeWidget = QTreeWidget(ListTemplateFormulas)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeWidget.setHeaderItem(__qtreewidgetitem)
        self.treeWidget.setObjectName(u"treeWidget")

        self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.addPushButton = QPushButton(ListTemplateFormulas)
        self.addPushButton.setObjectName(u"addPushButton")

        self.verticalLayout.addWidget(self.addPushButton)

        self.editPushButton = QPushButton(ListTemplateFormulas)
        self.editPushButton.setObjectName(u"editPushButton")

        self.verticalLayout.addWidget(self.editPushButton)

        self.upButton = QPushButton(ListTemplateFormulas)
        self.upButton.setObjectName(u"upButton")

        self.verticalLayout.addWidget(self.upButton)

        self.downButton = QPushButton(ListTemplateFormulas)
        self.downButton.setObjectName(u"downButton")

        self.verticalLayout.addWidget(self.downButton)

        self.removePushButton = QPushButton(ListTemplateFormulas)
        self.removePushButton.setObjectName(u"removePushButton")

        self.verticalLayout.addWidget(self.removePushButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.savePushButton = QPushButton(ListTemplateFormulas)
        self.savePushButton.setObjectName(u"savePushButton")

        self.horizontalLayout_3.addWidget(self.savePushButton)

        self.cancelPushButton = QPushButton(ListTemplateFormulas)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout_3.addWidget(self.cancelPushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.gridLayout_2.addLayout(self.verticalLayout_3, 0, 0, 1, 1)


        self.retranslateUi(ListTemplateFormulas)

        QMetaObject.connectSlotsByName(ListTemplateFormulas)
    # setupUi

    def retranslateUi(self, ListTemplateFormulas):
        ListTemplateFormulas.setWindowTitle(QCoreApplication.translate("ListTemplateFormulas", u"\u0421\u043f\u0438\u0441\u043e\u043a \u0448\u0430\u0431\u043b\u043e\u043d\u043d\u044b\u0445 \u0444\u043e\u0440\u043c\u0443\u043b", None))
        self.addParamsPushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0441\u0442\u0440\u043e\u043a\u0438 \u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u0443", None))
        self.helpToolButton.setToolTip(QCoreApplication.translate("ListTemplateFormulas", u"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c \u0438\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044e \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 \u0441 \u0444\u043e\u0440\u043c\u0443\u043b\u0430\u043c\u0438", None))
        self.helpToolButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"?", None))
        self.addPushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.editPushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c", None))
        self.upButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0412\u0432\u0435\u0440\u0445", None))
        self.downButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0412\u043d\u0438\u0437", None))
        self.removePushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.savePushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
        self.cancelPushButton.setText(QCoreApplication.translate("ListTemplateFormulas", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

