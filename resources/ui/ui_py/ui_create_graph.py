# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_graph.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_CreateGraphDialog(object):
    def setupUi(self, CreateGraphDialog):
        if not CreateGraphDialog.objectName():
            CreateGraphDialog.setObjectName(u"CreateGraphDialog")
        CreateGraphDialog.resize(564, 380)
        self.gridLayout = QGridLayout(CreateGraphDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_4 = QLabel(CreateGraphDialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_4.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label_4)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(CreateGraphDialog)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.nameLineEdit = QLineEdit(CreateGraphDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.verticalLayout.addLayout(self.formLayout)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_2 = QLabel(CreateGraphDialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label = QLabel(CreateGraphDialog)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.XComboBox = QComboBox(CreateGraphDialog)
        self.XComboBox.setObjectName(u"XComboBox")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.XComboBox)

        self.YComboBox = QComboBox(CreateGraphDialog)
        self.YComboBox.setObjectName(u"YComboBox")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.YComboBox)

        self.verticalLayout.addLayout(self.formLayout_2)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_5 = QLabel(CreateGraphDialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label_5.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label_5)

        self.defaultRadioButton = QRadioButton(CreateGraphDialog)
        self.defaultRadioButton.setObjectName(u"defaultRadioButton")
        self.defaultRadioButton.setChecked(True)

        self.verticalLayout_3.addWidget(self.defaultRadioButton)

        self.assemblyRadioButton = QRadioButton(CreateGraphDialog)
        self.assemblyRadioButton.setObjectName(u"assemblyRadioButton")

        self.verticalLayout_3.addWidget(self.assemblyRadioButton)

        self.modelRadioButton = QRadioButton(CreateGraphDialog)
        self.modelRadioButton.setObjectName(u"modelRadioButton")

        self.verticalLayout_3.addWidget(self.modelRadioButton)

        self.productRadioButton = QRadioButton(CreateGraphDialog)
        self.productRadioButton.setObjectName(u"productRadioButton")

        self.verticalLayout_3.addWidget(self.productRadioButton)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_6 = QLabel(CreateGraphDialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setWordWrap(True)

        self.verticalLayout_6.addWidget(self.label_6)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_10 = QLabel(CreateGraphDialog)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.comboBox = QComboBox(CreateGraphDialog)
        self.comboBox.setObjectName(u"comboBox")

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox)

        self.verticalLayout_6.addLayout(self.formLayout_5)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_7 = QLabel(CreateGraphDialog)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.fromDoubleSpinBox = QDoubleSpinBox(CreateGraphDialog)
        self.fromDoubleSpinBox.setObjectName(u"fromDoubleSpinBox")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.fromDoubleSpinBox)

        self.label_8 = QLabel(CreateGraphDialog)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.toDoubleSpinBox = QDoubleSpinBox(CreateGraphDialog)
        self.toDoubleSpinBox.setObjectName(u"toDoubleSpinBox")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.toDoubleSpinBox)

        self.verticalLayout_5.addLayout(self.formLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.acceptPushButton = QPushButton(CreateGraphDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.horizontalLayout.addWidget(self.acceptPushButton)

        self.deletePushButton = QPushButton(CreateGraphDialog)
        self.deletePushButton.setObjectName(u"deletePushButton")

        self.horizontalLayout.addWidget(self.deletePushButton)

        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.verticalLayout_6.addLayout(self.verticalLayout_5)

        self.verticalLayout_8.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_9 = QLabel(CreateGraphDialog)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setWordWrap(True)

        self.verticalLayout_7.addWidget(self.label_9)

        self.listWidget = QListWidget(CreateGraphDialog)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout_7.addWidget(self.listWidget)

        self.verticalLayout_8.addLayout(self.verticalLayout_7)

        self.horizontalLayout_2.addLayout(self.verticalLayout_8)

        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.buttonBox = QDialogButtonBox(CreateGraphDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.horizontalLayout_3.addWidget(self.buttonBox)

        self.verticalLayout_9.addLayout(self.horizontalLayout_3)

        self.gridLayout.addLayout(self.verticalLayout_9, 0, 0, 1, 1)

        self.retranslateUi(CreateGraphDialog)
        self.buttonBox.accepted.connect(CreateGraphDialog.accept)
        self.buttonBox.rejected.connect(CreateGraphDialog.reject)

        QMetaObject.connectSlotsByName(CreateGraphDialog)

    # setupUi

    def retranslateUi(self, CreateGraphDialog):
        CreateGraphDialog.setWindowTitle(QCoreApplication.translate("CreateGraphDialog",
                                                                    u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0433\u0440\u0430\u0444\u0438\u043a\u0430",
                                                                    None))
        self.label_4.setText(QCoreApplication.translate("CreateGraphDialog",
                                                        u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u0434\u043b\u044f \u043e\u0441\u0435\u0439 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442",
                                                        None))
        self.label_3.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.label_2.setText(QCoreApplication.translate("CreateGraphDialog", u"Y:", None))
        self.label.setText(QCoreApplication.translate("CreateGraphDialog", u"X:", None))
        self.label_5.setText(QCoreApplication.translate("CreateGraphDialog",
                                                        u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0439 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0430\u0445 \u043f\u043e \u0433\u0440\u0443\u043f\u043f\u0430\u043c ",
                                                        None))
        self.defaultRadioButton.setText(QCoreApplication.translate("CreateGraphDialog",
                                                                   u"\u041f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e",
                                                                   None))
        self.assemblyRadioButton.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u0421\u0431\u043e\u0440\u043a\u0430", None))
        self.modelRadioButton.setText(QCoreApplication.translate("CreateGraphDialog",
                                                                 u"\u041e\u043f\u044b\u0442\u043d\u044b\u0439 \u043e\u0431\u0440\u0430\u0437\u0435\u0446",
                                                                 None))
        self.productRadioButton.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u0418\u0437\u0434\u0435\u043b\u0438\u0435", None))
        self.label_6.setText(QCoreApplication.translate("CreateGraphDialog",
                                                        u"\u0412\u044b\u0431\u043e\u0440 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u0430 \u0434\u043b\u044f \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0434\u0438\u0430\u043f\u0430\u0437\u043e\u043d\u0430 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f ",
                                                        None))
        self.label_10.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435: ",
                                       None))
        self.label_7.setText(QCoreApplication.translate("CreateGraphDialog", u"\u041e\u0442:", None))
        self.label_8.setText(QCoreApplication.translate("CreateGraphDialog", u"\u0414\u043e:", None))
        self.acceptPushButton.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c", None))
        self.deletePushButton.setText(
            QCoreApplication.translate("CreateGraphDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.label_9.setText(QCoreApplication.translate("CreateGraphDialog",
                                                        u"\u0421\u043f\u0438\u0441\u043e\u043a \u0437\u0430\u0434\u0430\u043d\u043d\u044b\u0439 \u0443\u0441\u043b\u043e\u0432\u0438\u0439 \u0434\u043b\u044f \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f ",
                                                        None))
    # retranslateUi
