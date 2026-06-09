# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'approximation.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_ApproxDialog(object):
    def setupUi(self, ApproxDialog):
        if not ApproxDialog.objectName():
            ApproxDialog.setObjectName(u"ApproxDialog")
        ApproxDialog.resize(266, 123)
        self.verticalLayout = QVBoxLayout(ApproxDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.polyTypeLabel = QLabel(ApproxDialog)
        self.polyTypeLabel.setObjectName(u"polyTypeLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.polyTypeLabel)

        self.polyTypeComboBox = QComboBox(ApproxDialog)
        self.polyTypeComboBox.setObjectName(u"polyTypeComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.polyTypeComboBox.sizePolicy().hasHeightForWidth())
        self.polyTypeComboBox.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.polyTypeComboBox)

        self.degLabel = QLabel(ApproxDialog)
        self.degLabel.setObjectName(u"degLabel")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.degLabel)

        self.degSpinBox = QSpinBox(ApproxDialog)
        self.degSpinBox.setObjectName(u"degSpinBox")
        sizePolicy.setHeightForWidth(self.degSpinBox.sizePolicy().hasHeightForWidth())
        self.degSpinBox.setSizePolicy(sizePolicy)
        self.degSpinBox.setMaximum(20)
        self.degSpinBox.setValue(3)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.degSpinBox)

        self.label = QLabel(ApproxDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.nameLineEdit = QLineEdit(ApproxDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QDialogButtonBox(ApproxDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ApproxDialog)
        self.buttonBox.accepted.connect(ApproxDialog.accept)
        self.buttonBox.rejected.connect(ApproxDialog.reject)

        QMetaObject.connectSlotsByName(ApproxDialog)
    # setupUi

    def retranslateUi(self, ApproxDialog):
        ApproxDialog.setWindowTitle(QCoreApplication.translate("ApproxDialog", u"\u041f\u043e\u0441\u0442\u0440\u043e\u0435\u043d\u0438\u0435 \u0430\u043f\u043f\u0440\u043e\u043a\u0441\u0438\u043c\u0430\u0446\u0438\u0438", None))
        self.polyTypeLabel.setText(QCoreApplication.translate("ApproxDialog", u"\u0422\u0438\u043f \u043f\u043e\u043b\u0438\u043d\u043e\u043c\u0430", None))
        self.degLabel.setText(QCoreApplication.translate("ApproxDialog", u"\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0442\u0435\u043f\u0435\u043d\u044c", None))
        self.label.setText(QCoreApplication.translate("ApproxDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0440\u0438\u0432\u043e\u0439", None))
    # retranslateUi

