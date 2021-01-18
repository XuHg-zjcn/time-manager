#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
import sqlite3
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow
from Qt_GUI.layout import Ui_MainWindow
from Qt_GUI.pyqtgraph_plot import dt2dplot
from Qt_GUI.tabview import test
from commd_line.init_config import init_config
from sqlite_api.tables import CollTable
from sqlite_api.task_db import TaskTable, Plan
from my_libs.smart_strptime.my_datetime import sTimeRange

conf = init_config()
db_path = conf['init']['db_path']
conn = sqlite3.connect(db_path)
tdb = TaskTable(conn)
colls = CollTable(conn)


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

    def change_year(self):
        year = self.ui.year.value()
        tR = sTimeRange.M(year)
        self.start.setRange(tR)
        self.stop.setRange(tR)
        self.update_view()

    def update_view(self):
        year = self.ui.year.value()
        start = self.start.timestamp_tuple()
        stop = self.stop.timestamp_tuple()
        plans = tdb.get_conds_plans({'sta': start, 'end': stop})
        ivtree = plans.get_ivtree(lambda p: Plan(p))
        dt2p.update_ivtree(ivtree, year)


if __name__ == '__main__':
    tdb.print_doings()
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle('time-manager Date-Time 2D Image')
    ui = Ui_MainWindow()
    ui.setupUi(win)
    test(ui.tableWidget)
    dt2p = dt2dplot(ui.PlotWidget, colls)
    win.show()
    controller(ui)
    sys.exit(app.exec_())
