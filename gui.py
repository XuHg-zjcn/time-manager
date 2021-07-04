#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
from Qt_GUI.data_getter.data_plot import DataPlot
import sys
import datetime
import time

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from Qt_GUI.selector2 import Selector2

from Qt_GUI.add_task_gen import AddTaskGenDialog
from Qt_GUI.datetime2d.PointsItem import PointsItem
from Qt_GUI.layout import Ui_MainWindow
from sqlite_api.task_db import ColumnSetTasks, tdb
from sqlite_api.collect_data import cdt


class MyUi_MainWindow(Ui_MainWindow):
    """
    select data and display.
    """
    def build(self, app):
        self.selector.setupUi(self.selector)
        self.selector.build()
        self.plotitem_tab.build()
        self.dp = DataPlot(cdt, self.dt2d_plot, 'coll_data')
        # set current year
        self.dt2d_plot.build(app, self)
        self.dt2d_plot.select_rect.connect(self.selector.set2datetime)
        self.dt2d_plot.select_point.connect(self.selector.set1datetime)
        self.dt2d_plot.select_rect.connect(self.update_table)
        self.dt2d_plot.select_point.connect(self.update_table)
        tdb.print_doings()
        tdb.print_need()
        self.selector.year.valueChanged.connect(self.change_year)
        year = datetime.date.today().year
        self.selector.year.setValue(year)
        self.swap_xy.stateChanged.connect(self.dt2d_plot.set_swap)

        points = PointsItem(self.dt2d_plot)  # PointsItem test
        df = pd.DataFrame({'timestamp': [time.time(), time.time()+1000]})
        points.setDataFrame(df)
        self.dt2d_plot.addItem2('points', points)

    def change_year(self, year):
        """
        QSpinBox year valueChanged slot.
        set DT2DWidget year, select plans from Sqlite and draw.
        @param year: int (0-9999)
        """
        self.dt2d_plot.set_year(year)
        self.selector.set_year0101_1231(year)
        where_dict = self.selector.get_sql_where_dict()
        self.dp.update(where_dict)

    def update_table(self):
        where_dict = self.selector.get_sql_where_dict()
        plans = tdb.get_conds_plans(where_dict)
        print(plans)
        plans = plans.str_datetime()
        self.tableView.setDataFrame(plans, 'tasks', column_set_cls=ColumnSetTasks,
                                    sql_table=tdb)


if __name__ == '__main__':
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle('time-manager Date-Time 2D Image')
    dia = QDialog()
    dia.setWindowTitle('add task gen')
    ui = MyUi_MainWindow()
    ui.setupUi(win)
    ui.build(app)
    ud = AddTaskGenDialog(ui)
    ud.setupUi(dia)
    ud.build()
    win.show()
    ui.selector.add_task_gen.clicked.connect(dia.show)
    sys.exit(app.exec_())
