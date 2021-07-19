# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selector.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Selector(object):
    def setupUi(self, Selector):
        Selector.setObjectName("Selector")
        Selector.resize(429, 234)
        self.layoutWidget = QtWidgets.QWidget(Selector)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 427, 232))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.max_time = QtWidgets.QLineEdit(self.layoutWidget)
        self.max_time.setMaximumSize(QtCore.QSize(200, 16777215))
        self.max_time.setObjectName("max_time")
        self.gridLayout.addWidget(self.max_time, 3, 2, 1, 1)
        self.is_use_re = QtWidgets.QCheckBox(self.layoutWidget)
        self.is_use_re.setObjectName("is_use_re")
        self.gridLayout.addWidget(self.is_use_re, 4, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.state = QtWidgets.QComboBox(self.layoutWidget)
        self.state.setObjectName("state")
        self.gridLayout.addWidget(self.state, 5, 1, 1, 1)
        self.name1 = QtWidgets.QLineEdit(self.layoutWidget)
        self.name1.setObjectName("name1")
        self.gridLayout.addWidget(self.name1, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.name2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.name2.setMaximumSize(QtCore.QSize(180, 16777215))
        self.name2.setObjectName("name2")
        self.gridLayout.addWidget(self.name2, 4, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.min_time = QtWidgets.QLineEdit(self.layoutWidget)
        self.min_time.setMaximumSize(QtCore.QSize(200, 16777215))
        self.min_time.setObjectName("min_time")
        self.gridLayout.addWidget(self.min_time, 3, 1, 1, 1)
        self.is_include_sub = QtWidgets.QCheckBox(self.layoutWidget)
        self.is_include_sub.setObjectName("is_include_sub")
        self.gridLayout.addWidget(self.is_include_sub, 3, 3, 1, 1)
        self.x_setting = QtWidgets.QComboBox(self.layoutWidget)
        self.x_setting.setObjectName("x_setting")
        self.gridLayout.addWidget(self.x_setting, 2, 3, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.time_max = QtWidgets.QTimeEdit(self.layoutWidget)
        self.time_max.setCurrentSection(QtWidgets.QDateTimeEdit.HourSection)
        self.time_max.setObjectName("time_max")
        self.gridLayout.addWidget(self.time_max, 2, 2, 1, 1)
        self.date_min = QtWidgets.QDateEdit(self.layoutWidget)
        self.date_min.setObjectName("date_min")
        self.gridLayout.addWidget(self.date_min, 1, 1, 1, 1)
        self.time_min = QtWidgets.QTimeEdit(self.layoutWidget)
        self.time_min.setObjectName("time_min")
        self.gridLayout.addWidget(self.time_min, 2, 1, 1, 1)
        self.date_max = QtWidgets.QDateEdit(self.layoutWidget)
        self.date_max.setDateTime(QtCore.QDateTime(QtCore.QDate(2000, 12, 11), QtCore.QTime(0, 0, 0)))
        self.date_max.setObjectName("date_max")
        self.gridLayout.addWidget(self.date_max, 1, 2, 1, 1)
        self.year = QtWidgets.QSpinBox(self.layoutWidget)
        self.year.setMaximum(9999)
        self.year.setObjectName("year")
        self.gridLayout.addWidget(self.year, 0, 3, 1, 1)
        self.update_view = QtWidgets.QPushButton(self.layoutWidget)
        self.update_view.setMaximumSize(QtCore.QSize(16777215, 30))
        self.update_view.setObjectName("update_view")
        self.gridLayout.addWidget(self.update_view, 1, 3, 1, 1)
        self.add_task_gen = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_task_gen.sizePolicy().hasHeightForWidth())
        self.add_task_gen.setSizePolicy(sizePolicy)
        self.add_task_gen.setObjectName("add_task_gen")
        self.gridLayout.addWidget(self.add_task_gen, 5, 3, 1, 1)

        self.retranslateUi(Selector)
        QtCore.QMetaObject.connectSlotsByName(Selector)

    def retranslateUi(self, Selector):
        _translate = QtCore.QCoreApplication.translate
        Selector.setWindowTitle(_translate("Selector", "Form"))
        self.is_use_re.setText(_translate("Selector", "正则"))
        self.label_6.setText(_translate("Selector", "时长"))
        self.label_2.setText(_translate("Selector", "最小"))
        self.label_5.setText(_translate("Selector", "时间"))
        self.label.setText(_translate("Selector", "名称"))
        self.label_4.setText(_translate("Selector", "日期"))
        self.is_include_sub.setText(_translate("Selector", "含子任务"))
        self.label_7.setText(_translate("Selector", "状态"))
        self.label_3.setText(_translate("Selector", "最大"))
        self.time_max.setDisplayFormat(_translate("Selector", "hh:mm:ss"))
        self.time_min.setDisplayFormat(_translate("Selector", "hh:mm:ss"))
        self.update_view.setText(_translate("Selector", "更新"))
        self.add_task_gen.setText(_translate("Selector", "添加生成器"))