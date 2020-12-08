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

conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)


class controller:
    def __init__(self, ui):
        self.ui = ui
        year = datetime.now().year
        self.ui.year.setValue(year)
        self.change_year()
        self.ui.year.valueChanged.connect(lambda: self.change_year())
        self.ui.update_view.clicked.connect(lambda: self.update_view())

    def change_year(self):
        year = self.ui.year.value()
        sta = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        self.ui.min_sta.setDateTime(sta)
        self.ui.max_sta.setDateTime(end)
        self.ui.min_end.setDateTime(sta)
        self.ui.max_end.setDateTime(end)
        sta = sta.timestamp()
        end = end.timestamp()
        plans = tdb.get_aitem({'sta_time': (sta, end), 'end_time': (sta, end)})
        ivtree = plans.get_ivtree()
        dt2p.update_ivtree(ivtree)

    def update_view(self):
        sm = self.ui.min_sta.dateTime().toPyDateTime()
        sM = self.ui.max_sta.dateTime().toPyDateTime()
        em = self.ui.min_end.dateTime().toPyDateTime()
        eM = self.ui.max_end.dateTime().toPyDateTime()
        plans = tdb.get_aitem({'sta_time': (sm, sM), 'end_time': (em, eM)})
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
