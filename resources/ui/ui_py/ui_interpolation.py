# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interpolation.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_InterpolationDialog(object):
    def setupUi(self, InterpolationDialog):
        if not InterpolationDialog.objectName():
            InterpolationDialog.setObjectName(u"InterpolationDialog")
        InterpolationDialog.resize(343, 95)
        self.gridLayout = QGridLayout(InterpolationDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.label = QLabel(InterpolationDialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.nameLineEdit = QLineEdit(InterpolationDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.polyTypeLabel = QLabel(InterpolationDialog)
        self.polyTypeLabel.setObjectName(u"polyTypeLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.polyTypeLabel)

        self.polyTypeComboBox = QComboBox(InterpolationDialog)
        self.polyTypeComboBox.setObjectName(u"polyTypeComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.polyTypeComboBox.sizePolicy().hasHeightForWidth())
        self.polyTypeComboBox.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.polyTypeComboBox)


        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(InterpolationDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(InterpolationDialog)
        self.buttonBox.accepted.connect(InterpolationDialog.accept)
        self.buttonBox.rejected.connect(InterpolationDialog.reject)

        QMetaObject.connectSlotsByName(InterpolationDialog)
    # setupUi

    def retranslateUi(self, InterpolationDialog):
        InterpolationDialog.setWindowTitle(QCoreApplication.translate("InterpolationDialog", u"\u041f\u043e\u0441\u0442\u0440\u043e\u0435\u043d\u0438\u0435 \u0438\u043d\u0442\u0435\u0440\u043f\u043e\u043b\u044f\u0446\u0438\u0438", None))
        self.label.setText(QCoreApplication.translate("InterpolationDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0440\u0438\u0432\u043e\u0439", None))
        self.polyTypeLabel.setText(QCoreApplication.translate("InterpolationDialog", u"\u0422\u0438\u043f \u043f\u043e\u043b\u0438\u043d\u043e\u043c\u0430", None))
    # retranslateUi

