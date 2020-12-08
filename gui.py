#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
from Qt_GUI.pyqtgraph_plot import dt2p, ui, app
from datetime import datetime
from commd_line.init_config import init_config
from sqlite_api.TODO_db import TODO_db

conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)

class controller:
    def __init__(self, win):
        self.win = win
        win.year.setValue(datetime.now().year)
        win.year.valueChanged.connect(lambda: self.change_year())
        win.update_view.clicked.connect(lambda: self.update())

    def change_year(self):
        year = self.win.year.value()
        sta = datetime(year, 1, 1).timestamp()
        end = datetime(year, 12, 31).timestamp()
        plans = tdb.get_aitem({'sta_time': (sta, end), 'end_time': (sta, end)})
        ivtree = plans.get_ivtree()
        dt2p.update_ivtree(ivtree)

    def update_view(self):
        pass

controller(ui)
sys.exit(app.exec_())
