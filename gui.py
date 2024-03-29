#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
from Qt_GUI.add_plot2 import AddPlot2
import sys
import datetime
import time

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from Qt_GUI.selector2 import Selector2
import IPython

from Qt_GUI.add_task_gen import AddTaskGenDialog
from Qt_GUI.plotitems.PointsItem import PointsItem
from Qt_GUI.layout import Ui_MainWindow
from sqlite_api.task_db import ColumnSetTasks, tdb
from sqlite_api.collect_data import cdt
from Qt_GUI.add_plot2 import ptab
from Qt_GUI.plotitems.IntervalsItem import DateTime2DItem


class MyUi_MainWindow(Ui_MainWindow):
    """
    select data and display.
    """
    def build(self, app):
        self.selector.setupUi(self.selector)
        self.selector.build()
        self.plotitem_tab.build()

        dia1 = QDialog()
        dia1.setWindowTitle('add task gen')
        ud = AddTaskGenDialog(ui)
        ud.setupUi(dia1)
        ud.build()
        self.selector.add_task_gen.clicked.connect(lambda x: dia1.show())

        dia2 = QDialog()
        dia2.setWindowTitle('add plot item')
        self.plotitem_tab.addreq.connect(lambda : dia2.show())

        # set current year
        self.dt2d_plot.build(app)
        self.dt2d_plot.select_rect.connect(self.selector.set2datetime)
        self.dt2d_plot.select_point.connect(self.selector.set1datetime)
        self.dt2d_plot.select_rect.connect(self.update_table)
        self.dt2d_plot.select_point.connect(self.update_table)
        self.plotitem_tab.dele.connect(lambda x: self.remove_item(x))
        self.sta_ipython.clicked.connect(lambda :IPython.embed(colors='Neutral'))
        tdb.print_doings()
        tdb.print_need()
        self.selector.year.valueChanged.connect(self.change_year)
        year = datetime.date.today().year
        self.selector.year.setValue(year)
        self.swap_xy.stateChanged.connect(self.set_swap)

        points = PointsItem()  # PointsItem test
        points.setTimestampList([time.time(), time.time()+1000])
        self.addItem('points', points)

        ap = AddPlot2()
        ap.setupUi(dia2)
        ap.build(self)

    def set_swap(self, new_state):
        self.dt2d_plot.set_swap(new_state)
        for item in self.plotitem_tab.values():
            item.set_swap()

    def change_year(self, year):
        """
        QSpinBox year valueChanged slot.
        set DT2DWidget year, select plans from Sqlite and draw.
        @param year: int (0-9999)
        """
        self.dt2d_plot.set_year(year)
        self.selector.set_year0101_1231(year)

    def update_table(self):
        where_dict = self.selector.get_sql_where_dict()
        plans = tdb.get_conds_plans(where_dict)
        print(plans)
        plans = plans.str_datetime()
        self.tableView.setDataFrame(plans, 'tasks', column_set_cls=ColumnSetTasks,
                                    sql_table=tdb)

    def addItem(self, name, item):
        if name in self.plotitem_tab:   # remove same name item if exist
            self.remove_item(name)
        item.update_xy(self.dt2d_plot.time2xy)
        self.plotitem_tab[name] = item
        self.dt2d_plot.addItem(item)

    def remove_item(self, name):
        """
        remove showing item.
        @param name: name of item
        """
        self.dt2d_plot.removeItem(self.plotitem_tab.pop(name))
        ptab.update_conds({'name':name}, {'show':False})

    def clear_items(self):
        """clear all items in the Widget."""
        # don't edit to remove item by `self.remove_item()`, else raise this error:
        # RuntimeError: dictionary changed size during iteration
        for item in self.plotitem_tab.values():
            self.dt2d_plot.removeItem(item)
        self.plotitem_tab.clear()
        ptab.update_conds(None, {'show':False})

    def draw_ivtree(self, ivt_color, default_color=0x00ffff, name=None, z=0):
        """
        draw ivtree datetime2d.
        @param ivt_color:     see DateTime2DItem.__init__
        @param default_color: see DateTime2DItem.__init__
        @param name: optional, None will default item
        @param z: ZValue(layer) of pyqtgraph PlotItem
        """
        item_new = DateTime2DItem(ivt_color, default_color)
        item_new.setZValue(z)
        self.addItem(name, item_new)
        #self.set_XY_full_range()

    def draw_points(self, lst, color=0x00ff00, name='points', *args, **kwargs):
        item_new = PointsItem()
        item_new.setTimestampList(lst, pen=color, brush=color, *args, **kwargs)
        self.addItem(name, item_new)

    def draw_points_label(self, lst, labels, color=0x00ff00, name='points_lable', *args, **kwargs):
        item_new = PointsItem()
        item_new.setMaskColor(color=color)
        item_new.setTsLabel(lst, labels, *args, **kwargs)
        self.addItem(name, item_new)

if __name__ == '__main__':
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle('time-manager Date-Time 2D Image')
    ui = MyUi_MainWindow()
    ui.setupUi(win)
    ui.build(app)
    win.show()
    sys.exit(app.exec_())
