# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_plot.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(266, 206)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(80, 160, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 241, 140))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.combo_param = QtWidgets.QComboBox(self.formLayoutWidget)
        self.combo_param.setEditable(True)
        self.combo_param.setObjectName("combo_param")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.combo_param)
        self.combo_func = QtWidgets.QComboBox(self.formLayoutWidget)
        self.combo_func.setEditable(True)
        self.combo_func.setObjectName("combo_func")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.combo_func)
        self.label_func = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_func.setObjectName("label_func")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_func)
        self.label_param = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_param.setObjectName("label_param")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_param)
        self.label_color = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_color.setObjectName("label_color")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_color)
        self.lineEdit_color = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_color.setObjectName("lineEdit_color")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_color)
        self.label_name = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_name.setObjectName("label_name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_name)
        self.combo_name = QtWidgets.QComboBox(self.formLayoutWidget)
        self.combo_name.setEditable(True)
        self.combo_name.setObjectName("combo_name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.combo_name)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_func.setText(_translate("Dialog", "函数"))
        self.label_param.setText(_translate("Dialog", "参数"))
        self.label_color.setText(_translate("Dialog", "颜色"))
        self.label_name.setText(_translate("Dialog", "名称"))
