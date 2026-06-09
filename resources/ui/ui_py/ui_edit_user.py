# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_user.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_EditUser(object):
    def setupUi(self, EditUser):
        if not EditUser.objectName():
            EditUser.setObjectName(u"EditUser")
        EditUser.resize(464, 485)
        self.gridLayout_2 = QGridLayout(EditUser)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_3 = QLabel(EditUser)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.usernameLineEdit_2 = QLineEdit(EditUser)
        self.usernameLineEdit_2.setObjectName(u"usernameLineEdit_2")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.usernameLineEdit_2)

        self.label_2 = QLabel(EditUser)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.nameLineEdit = QLineEdit(EditUser)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.nameLineEdit)

        self.label_4 = QLabel(EditUser)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.surnameLineEdit = QLineEdit(EditUser)
        self.surnameLineEdit.setObjectName(u"surnameLineEdit")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.surnameLineEdit)

        self.label_5 = QLabel(EditUser)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.activeCheckBox = QCheckBox(EditUser)
        self.activeCheckBox.setObjectName(u"activeCheckBox")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.activeCheckBox)

        self.label_6 = QLabel(EditUser)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.lastLoginLineEdit = QLineEdit(EditUser)
        self.lastLoginLineEdit.setObjectName(u"lastLoginLineEdit")
        self.lastLoginLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lastLoginLineEdit)

        self.label_7 = QLabel(EditUser)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.lastLogoutLineEdit = QLineEdit(EditUser)
        self.lastLogoutLineEdit.setObjectName(u"lastLogoutLineEdit")
        self.lastLogoutLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.FieldRole, self.lastLogoutLineEdit)

        self.label_9 = QLabel(EditUser)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.spinBox_2 = QSpinBox(EditUser)
        self.spinBox_2.setObjectName(u"spinBox_2")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.spinBox_2)

        self.label_8 = QLabel(EditUser)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.spinBox = QSpinBox(EditUser)
        self.spinBox.setObjectName(u"spinBox")

        self.formLayout_2.setWidget(8, QFormLayout.ItemRole.FieldRole, self.spinBox)

        self.label_11 = QLabel(EditUser)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_2.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.leftSpinBox = QSpinBox(EditUser)
        self.leftSpinBox.setObjectName(u"leftSpinBox")

        self.formLayout_2.setWidget(9, QFormLayout.ItemRole.FieldRole, self.leftSpinBox)

        self.label_10 = QLabel(EditUser)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.deletedCheckBox = QCheckBox(EditUser)
        self.deletedCheckBox.setObjectName(u"deletedCheckBox")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.deletedCheckBox)

        self.verticalLayout.addLayout(self.formLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.line = QFrame(EditUser)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.label = QLabel(EditUser)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeView = QTreeView(EditUser)
        self.treeView.setObjectName(u"treeView")

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.addButton = QPushButton(EditUser)
        self.addButton.setObjectName(u"addButton")

        self.verticalLayout_2.addWidget(self.addButton)

        self.removeButton = QPushButton(EditUser)
        self.removeButton.setObjectName(u"removeButton")

        self.verticalLayout_2.addWidget(self.removeButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout)

        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox_2 = QDialogButtonBox(EditUser)
        self.buttonBox_2.setObjectName(u"buttonBox_2")
        self.buttonBox_2.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox_2.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox_2)

        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(EditUser)

        QMetaObject.connectSlotsByName(EditUser)

    # setupUi

    def retranslateUi(self, EditUser):
        EditUser.setWindowTitle(QCoreApplication.translate("EditUser",
                                                           u"\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u043c",
                                                           None))
        self.label_3.setText(QCoreApplication.translate("EditUser", u"\u041b\u043e\u0433\u0438\u043d:", None))
        self.label_2.setText(QCoreApplication.translate("EditUser", u"\u0418\u043c\u044f:", None))
        self.label_4.setText(
            QCoreApplication.translate("EditUser", u"\u0424\u0430\u043c\u0438\u043b\u0438\u044f:", None))
        self.label_5.setText(
            QCoreApplication.translate("EditUser", u"\u0410\u043a\u0442\u0438\u0432\u0435\u043d:", None))
        self.activeCheckBox.setText("")
        self.label_6.setText(QCoreApplication.translate("EditUser",
                                                        u"\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u0432\u0445\u043e\u0434:",
                                                        None))
        self.label_7.setText(QCoreApplication.translate("EditUser",
                                                        u"\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 \u0432\u044b\u0445\u043e\u0434:",
                                                        None))
        self.label_9.setText(QCoreApplication.translate("EditUser",
                                                        u"\u041f\u0440\u0438\u043d\u0443\u0434\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0447\u0435\u0440\u0435\u0437 (\u043c\u0438\u043d\u0443\u0442\u044b):",
                                                        None))
        self.label_8.setText(QCoreApplication.translate("EditUser",
                                                        u"\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u043f\u044b\u0442\u043e\u043a \u0434\u043b\u044f \u0432\u0445\u043e\u0434\u0430: ",
                                                        None))
        self.label_11.setText(QCoreApplication.translate("EditUser",
                                                         u"\u041e\u0441\u0442\u0430\u0432\u0448\u0435\u0435\u0441\u044f \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u043f\u044b\u0442\u043e\u043a:",
                                                         None))
        self.label_10.setText(QCoreApplication.translate("EditUser",
                                                         u"\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d:",
                                                         None))
        self.deletedCheckBox.setText("")
        self.label.setText(QCoreApplication.translate("EditUser",
                                                      u"\u0420\u043e\u043b\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
                                                      None))
        self.addButton.setText(
            QCoreApplication.translate("EditUser", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c", None))
        self.removeButton.setText(
            QCoreApplication.translate("EditUser", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
    # retranslateUi
