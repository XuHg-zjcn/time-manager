#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from Qt_GUI.layout import Ui_MainWindow
from Qt_GUI.pyqtgraph_plot import dt2dplot
from datetime import datetime
from commd_line.init_config import init_config
from sqlite_api.TODO_db import TODO_db
from smart_strptime.my_datetime import sTimeRange

conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)

class QTimeRange(sTimeRange):
    def __new__(cls, widget_begin, widget_end):
        self = super().__new__(QTimeRange, None, None)
        widget_begin.dateTimeChanged.connect(lambda: self.update_begin())
        widget_end.dateTimeChanged.connect(lambda: self.update_end())
        self.widget_begin = widget_begin
        self.widget_end = widget_end
        self.update_begin()
        self.update_end()
        return self

    def update_begin(self):
        self._begin = self.widget_begin.dateTime().toPyDateTime()

    def update_end(self):
        self._end = self.widget_end.dateTime().toPyDateTime()

    def setRange(self, begin, end=None):
        if isinstance(begin, sTimeRange):
            self._begin = begin._begin
            self._end = begin._end
        else:
            self._begin = begin
            self._end = end
        self.widget_begin.setDateTime(self._begin)
        self.widget_end.setDateTime(self._end)

class controller:
    def __init__(self, ui):
        self.ui = ui
        self.start = QTimeRange(self.ui.min_sta, self.ui.max_sta)
        self.stop = QTimeRange(self.ui.min_end, self.ui.max_end)
        self.ui.year.valueChanged.connect(lambda: self.change_year())
        self.ui.update_view.clicked.connect(lambda: self.update_view())
        # set current year
        year = datetime.now().year
        self.ui.year.setValue(year)
        self.change_year()

    def change_year(self):
        year = self.ui.year.value()
        tR = sTimeRange.M(year)
        self.start.setRange(tR)
        self.stop.setRange(tR)
        t_range = tR.timestamp_tuple()
        plans = tdb.get_aitem({'sta_time': t_range, 'end_time': t_range})
        ivtree = plans.get_ivtree()
        dt2p.update_ivtree(ivtree)

    def update_view(self):
        start = self.start.timestamp_tuple()
        end = self.start.timestamp_tuple()
        plans = tdb.get_aitem({'sta_time': start, 'end_time': end})
        ivtree = plans.get_ivtree()
        dt2p.update_ivtree(ivtree)

app = QApplication([])
win = QMainWindow()
win.setWindowTitle('time-manager Date-Time 2D Image')
ui = Ui_MainWindow()
ui.setupUi(win)
dt2p = dt2dplot(ui.PlotView, 2020)
win.show()
controller(ui)
sys.exit(app.exec_())
