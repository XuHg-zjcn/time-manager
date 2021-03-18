#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
import datetime
import time

import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog,\
    QDateEdit, QTimeEdit, QComboBox

from Qt_GUI.add_task_gen import AddTaskGenDialog
from Qt_GUI.datetime2d.PointsItem import PointsItem
from Qt_GUI.layout import Ui_MainWindow
from my_libs.datetime_utils import date2ts0, time2float
from sqlite_api.tables import colls
from sqlite_api.task_db import ColumnSetTasks, tdb, Plan


class DateTimeRange(QObject):
    change = pyqtSignal()
    settings = ['2D包含',  # a< Ds<De <b && {(c< Ts<Te <d) if (Ds==De) else (c=0,d=24)}
                '2D重叠',  # (Ts<=d && c<=Te) if Ds==De, else omitted
                '1D包含',  # (a,c) <= sta <= end <= (b,d)'
                '1D重叠',  # [(a,c), (b,d)] overlaps [sta, end]
                '点选择']  # sta < (a,c) < end

    def __init__(self, dm: QDateEdit, dM: QDateEdit,
                       tm: QTimeEdit, tM: QTimeEdit,
                       comb: QComboBox):
        super().__init__()
        self.dm = dm
        self.dM = dM
        self.tm = tm
        self.tM = tM
        self.comb = comb
        dm.dateChanged.connect(self.change.emit)
        dM.dateChanged.connect(self.change.emit)
        tm.timeChanged.connect(self.change.emit)
        tM.timeChanged.connect(self.change.emit)
        comb.currentIndexChanged.connect(self.change.emit)
        self.comb.clear()
        self.comb.addItems(self.settings)
        self.comb.currentIndexChanged.connect(self.comb_slot)
        self.default4dt_comb_index = 0

    def comb_slot(self, index):
        is_enable = index != 4
        self.dM.setEnabled(is_enable)
        self.tM.setEnabled(is_enable)
        if is_enable:
            self.default4dt_comb_index = index

    def get4py(self):
        dm_ = self.dm.date().toPyDate()
        dM_ = self.dM.date().toPyDate()
        tm_ = self.tm.time().toPyTime()
        tM_ = self.tM.time().toPyTime()
        return dm_, dM_, tm_, tM_

    def get2py(self):
        dm, dM, tm, tM = self.get4py()
        m = datetime.datetime.combine(dm, tm)
        M = datetime.datetime.combine(dM, tM)
        return m, M

    def get2float(self):
        m, M = self.get2py()
        return m.timestamp(), M.timestamp()

    def get4float(self):
        dm, dM, tm, tM = self.get4py()
        dmf = date2ts0(dm)
        dMf = date2ts0(dM)
        tmf = time2float(tm)
        tMf = time2float(tM)
        return dmf, dMf, tmf, tMf

    def get4str(self):
        dm_ = self.dm.date().toString('yyyy-MM-dd')
        dM_ = self.dM.date().toString('yyyy-MM-dd')
        tm_ = self.tm.time().toString('hh:mm:ss')
        tM_ = self.tM.time().toString('hh:mm:ss')
        return dm_, dM_, tm_, tM_

    def set2datetime(self, m, M):
        d1 = m.date()
        d2 = M.date()
        t1 = m.time()
        t2 = M.time()
        self.dm.setDate(min(d1, d2))
        self.dM.setDate(max(d1, d2))
        self.tm.setTime(min(t1, t2))
        self.tM.setTime(max(t1, t2))
        if self.comb.currentIndex() == 4:
            self.comb.setCurrentIndex(self.default4dt_comb_index)

    def set1datetime(self, m):
        self.comb.setCurrentIndex(4)
        self.dm.setDate(m.date())
        self.tm.setTime(m.time())

    def set_year0101_1231(self, year):
        d0101 = datetime.datetime(year, 1,  1,  0,  0,  0)
        d1231 = datetime.datetime(year, 12, 31, 23, 59, 59)
        self.set2datetime(d0101, d1231)

    def get_sql_where_dict(self):
        # TODO: timezone
        name = self.comb.currentText()
        dm, dM, tm, tM = self.get4str()
        m, M = self.get2float()
        if name == '2D包含':
            if tm == '00:00:00' and tM == '23:59:59':
                ret = {'sta': ('>=', m), 'end': ('<=', M)}  # same to '1D包含'
            else:
                dmf, dMf, tmf, tMf = self.get4float()
                ret = {'sta': ('>=', dmf),
                       'end': ('<=', dMf),
                       '(sta+8*3600)%86400': ('>=', tmf),
                       '(end+8*3600)%86400': ('<=', tMf),
                       'CAST((end+8*3600)/86400 as int)=CAST((sta+8*3600)/86400 as int)': []}
        elif name == '2D重叠':
            dmf, dMf, tmf, tMf = self.get4float()
            w_str = ('sta>=? AND end<? AND (sta+8*3600)%86400<? AND (end+8*3600)%86400>? OR '
                     # date of end != date of start
                     '((sta+8*3600)%86400<=? AND sta>=? AND sta<? OR '
                     '(end+8*3600)%86400>? AND end>=? AND end<?) AND '
                     'CAST((end+8*3600)/86400 as int)!=CAST((sta+8*3600)/86400 as int) OR '
                     # date of end > date of start + 1
                     'end>=?+86400 AND sta<?-86400 AND '
                     'CAST((end+8*3600)/86400 as int)>CAST((sta+8*3600)/86400 as int)+1')
            w_paras = [dmf, dMf, tMf, tmf, tMf, dmf, dMf, tmf, dmf, dMf, dmf, dMf]
            ret = {w_str: w_paras}
        elif name == '1D包含':
            ret = {'sta': ('>=', m), 'end': ('<=', M)}
        elif name == '1D重叠':
            ret = {'sta': ('<=', M), 'end': ('>=', m)}
        elif name == '点选择':
            ret = {'sta': ('<=', m), 'end': ('>=', m)}
        else:
            raise ValueError('ComboBox get unknown name')
        return ret


class MyUi_MainWindow(Ui_MainWindow):
    """
    select data and display.
    """

    def build(self, app):
        self.rang = DateTimeRange(self.date_min, self.date_max,
                                  self.time_min, self.time_max,
                                  self.x_setting)
        # set current year
        self.dt2d_plot.build(app, colls)
        self.dt2d_plot.select_rect.connect(self.rang.set2datetime)
        self.dt2d_plot.select_point.connect(self.rang.set1datetime)
        self.dt2d_plot.select_rect.connect(self.update_table)
        self.dt2d_plot.select_point.connect(self.update_table)
        self.cluster.clicked.connect(self.dt2d_plot.start_cluster)
        tdb.print_doings()
        tdb.print_need()
        self.year.valueChanged.connect(self.change_year)
        year = datetime.date.today().year
        self.year.setValue(year)
        self.swap_xy.stateChanged.connect(self.dt2d_plot.set_swap)

        points = PointsItem(self.dt2d_plot)  # PointsItem test
        df = pd.DataFrame({'timestamp': [time.time(), time.time()+1000]})
        points.setDataFrame(df)
        self.dt2d_plot.addItem2('points', points)

    def change_year(self, year):
        self.rang.set_year0101_1231(year)
        where_dict = self.rang.get_sql_where_dict()
        plans = tdb.get_conds_plans(where_dict)
        self.dt2d_plot.set_year(year)
        ivt_color = plans.get_ivtree(lambda p: Plan(p).get_collect_color(colls))
        self.dt2d_plot.draw_ivtree(ivt_color)

    def update_table(self):
        where_dict = self.rang.get_sql_where_dict()
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
    ui.add_task_gen.clicked.connect(dia.show)
    sys.exit(app.exec_())
