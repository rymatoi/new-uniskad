# -*- coding: utf-8 -*-

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_CreateEpureDialog(object):
    def setupUi(self, CreateEpureDialog):
        if not CreateEpureDialog.objectName():
            CreateEpureDialog.setObjectName(u"CreateEpureDialog")
        CreateEpureDialog.resize(720, 560)
        CreateEpureDialog.setMinimumSize(QSize(640, 500))
        self.mainLayout = QVBoxLayout(CreateEpureDialog)
        self.mainLayout.setObjectName(u"mainLayout")
        self.headerFormLayout = QFormLayout()
        self.headerFormLayout.setObjectName(u"headerFormLayout")
        self.headerFormLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.label_4 = QLabel(CreateEpureDialog)
        self.label_4.setObjectName(u"label_4")

        self.headerFormLayout.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.nameLineEdit = QLineEdit(CreateEpureDialog)
        self.nameLineEdit.setObjectName(u"nameLineEdit")

        self.headerFormLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.mainLayout.addLayout(self.headerFormLayout)

        self.descriptionLabel = QLabel(CreateEpureDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.mainLayout.addWidget(self.descriptionLabel)

        self.axisGroupBox = QGroupBox(CreateEpureDialog)
        self.axisGroupBox.setObjectName(u"axisGroupBox")
        self.axisLayout = QVBoxLayout(self.axisGroupBox)
        self.axisLayout.setObjectName(u"axisLayout")
        self.axisHintLabel = QLabel(self.axisGroupBox)
        self.axisHintLabel.setObjectName(u"axisHintLabel")
        self.axisHintLabel.setWordWrap(True)

        self.axisLayout.addWidget(self.axisHintLabel)

        self.paramsTreeView = QTreeView(self.axisGroupBox)
        self.paramsTreeView.setObjectName(u"paramsTreeView")
        self.paramsTreeView.setAlternatingRowColors(True)
        self.paramsTreeView.setRootIsDecorated(False)
        self.paramsTreeView.setHeaderHidden(True)
        self.paramsTreeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.paramsTreeView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.axisLayout.addWidget(self.paramsTreeView)

        self.axisButtonsLayout = QHBoxLayout()
        self.axisButtonsLayout.setObjectName(u"axisButtonsLayout")
        self.addParamPushButton = QPushButton(self.axisGroupBox)
        self.addParamPushButton.setObjectName(u"addParamPushButton")

        self.axisButtonsLayout.addWidget(self.addParamPushButton)

        self.removeParamPushButton = QPushButton(self.axisGroupBox)
        self.removeParamPushButton.setObjectName(u"removeParamPushButton")

        self.axisButtonsLayout.addWidget(self.removeParamPushButton)

        self.axisButtonsSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.axisButtonsLayout.addItem(self.axisButtonsSpacer)

        self.axisLayout.addLayout(self.axisButtonsLayout)

        self.mainLayout.addWidget(self.axisGroupBox)

        self.extraParamGroupBox = QGroupBox(CreateEpureDialog)
        self.extraParamGroupBox.setObjectName(u"extraParamGroupBox")
        self.extraParamLayout = QVBoxLayout(self.extraParamGroupBox)
        self.extraParamLayout.setObjectName(u"extraParamLayout")
        self.extraParamHintLabel = QLabel(self.extraParamGroupBox)
        self.extraParamHintLabel.setObjectName(u"extraParamHintLabel")
        self.extraParamHintLabel.setWordWrap(True)

        self.extraParamLayout.addWidget(self.extraParamHintLabel)

        self.extraParamSelectionLayout = QHBoxLayout()
        self.extraParamSelectionLayout.setObjectName(u"extraParamSelectionLayout")
        self.selectParam = QPushButton(self.extraParamGroupBox)
        self.selectParam.setObjectName(u"selectParam")

        self.extraParamSelectionLayout.addWidget(self.selectParam)

        self.paramValuesLineEdit = QLineEdit(self.extraParamGroupBox)
        self.paramValuesLineEdit.setObjectName(u"paramValuesLineEdit")
        self.paramValuesLineEdit.setReadOnly(True)

        self.extraParamSelectionLayout.addWidget(self.paramValuesLineEdit)

        self.extraParamLayout.addLayout(self.extraParamSelectionLayout)

        self.mainLayout.addWidget(self.extraParamGroupBox)

        self.footerLayout = QHBoxLayout()
        self.footerLayout.setObjectName(u"footerLayout")
        self.oySetupPushButton = QPushButton(CreateEpureDialog)
        self.oySetupPushButton.setObjectName(u"oySetupPushButton")

        self.footerLayout.addWidget(self.oySetupPushButton)

        self.footerSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.footerLayout.addItem(self.footerSpacer)

        self.acceptPushButton = QPushButton(CreateEpureDialog)
        self.acceptPushButton.setObjectName(u"acceptPushButton")

        self.footerLayout.addWidget(self.acceptPushButton)

        self.cancelPushButton = QPushButton(CreateEpureDialog)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.footerLayout.addWidget(self.cancelPushButton)

        self.mainLayout.addLayout(self.footerLayout)

        self.retranslateUi(CreateEpureDialog)

        QMetaObject.connectSlotsByName(CreateEpureDialog)

    # setupUi

    def retranslateUi(self, CreateEpureDialog):
        CreateEpureDialog.setWindowTitle(QCoreApplication.translate("CreateEpureDialog", u"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043f\u043e\u043b\u0435\u0439", None))
        self.label_4.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.nameLineEdit.setPlaceholderText(QCoreApplication.translate("CreateEpureDialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0435\u043c\u043e\u0433\u043e \u043f\u043e\u043b\u044f", None))
        self.descriptionLabel.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u043e\u043a\u043d\u043e \u0434\u043b\u044f \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0438 \u043d\u043e\u0432\u043e\u0439 \u044d\u043f\u044e\u0440\u044b: \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u0434\u0438\u043d \u0438\u043b\u0438 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u043e\u0432 \u043e\u0441\u0438 X, \u043f\u0440\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u0438 \u0443\u043a\u0430\u0436\u0438\u0442\u0435 \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u0438 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u0442\u0435 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u043e\u0441\u0438 OY.", None))
        self.axisGroupBox.setTitle(QCoreApplication.translate("CreateEpureDialog", u"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043e\u0441\u0438 X", None))
        self.axisHintLabel.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u044e\u0442\u0441\u044f \u0432 \u0441\u043f\u0438\u0441\u043a\u0435. \u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u00ab\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u2026\u00bb, \u0447\u0442\u043e\u0431\u044b \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f. \u0414\u043b\u044f \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u044f \u0432\u043e\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\u0441\u044c \u043a\u043d\u043e\u043f\u043a\u043e\u0439 \u00ab\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0435\u00bb.", None))
        self.addParamPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u2026", None))
        self.removeParamPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0435", None))
        self.extraParamGroupBox.setTitle(QCoreApplication.translate("CreateEpureDialog", u"\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440", None))
        self.extraParamHintLabel.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041d\u0435\u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440 \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442 \u0443\u0442\u043e\u0447\u043d\u0438\u0442\u044c \u0434\u0430\u043d\u043d\u044b\u0435 \u044d\u043f\u044e\u0440\u044b. \u041f\u043e\u0441\u043b\u0435 \u0432\u044b\u0431\u043e\u0440\u0430 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u044b \u043d\u0438\u0436\u0435.", None))
        self.selectParam.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u043f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u2026", None))
        self.paramValuesLineEdit.setPlaceholderText(QCoreApplication.translate("CreateEpureDialog", u"\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u044b \u0437\u0434\u0435\u0441\u044c", None))
        self.oySetupPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0438\u0442\u044c \u043e\u0441\u044c OY\u2026", None))
        self.acceptPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c", None))
        self.cancelPushButton.setText(QCoreApplication.translate("CreateEpureDialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

