#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from Qt_GUI.add_task_gen import Ui_Dialog

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QDateEdit, QTimeEdit, QComboBox
from Qt_GUI.layout import Ui_MainWindow
from Qt_GUI.pyqtgraph_plot import DT2DPlot, SelectRect
from commd_line.init_config import conn
from my_libs.datetime_utils import date2ts0, time2float
from sqlite_api.tables import CollTable
from sqlite_api.task_db import TaskTable, Plan, Plans, ColumnSetTasks


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
        self.comb.currentTextChanged.connect(self.comb_slot)

    def comb_slot(self, text):
        is_enable = text != '点选择'
        self.dM.setEnabled(is_enable)
        self.tM.setEnabled(is_enable)

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

    def get_sql_where_dict(self):
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
            where_str = ('sta>=? AND end<? AND (sta+8*3600)%86400<? AND (end+8*3600)%86400>? OR '
                         # date of end != date of start
                         '((sta+8*3600)%86400<=? AND sta>=? AND sta<? OR '
                         '(end+8*3600)%86400>? AND end>=? AND end<?) AND '
                         'CAST((end+8*3600)/86400 as int)!=CAST((sta+8*3600)/86400 as int) OR '
                         # date of end > date of start + 1
                         'end>=?+86400 AND sta<?-86400 AND '
                         'CAST((end+8*3600)/86400 as int)>CAST((sta+8*3600)/86400 as int)+1')
            where_paras = [dmf, dMf, tMf, tmf, tMf, dmf, dMf, tmf, dmf, dMf, dmf, dMf]
            ret = {where_str: where_paras}
        elif name == '1D包含':
            ret = {'sta': ('>=', m), 'end': ('<=', M)}
        elif name == '1D重叠':
            ret = {'sta': ('<=', M), 'end': ('>=', m)}
        elif name == '点选择':
            ret = {'sta': ('<=', m), 'end': ('>=', m)}
        else:
            raise ValueError('ComboBox get unknown name')
        return ret


class Controller:
    """
    select data and display.
    """

    def __init__(self, ui, app):
        self.ui = ui
        self.rang = DateTimeRange(self.ui.date_min, self.ui.date_max,
                                  self.ui.time_min, self.ui.time_max,
                                  self.ui.x_setting)
        # set current year
        year = datetime.date.today().year
        self.ui.year.setValue(year)
        self.table = ui.tableView
        self.tdb = TaskTable(conn)
        self.colls = CollTable(conn)
        self.dt2p = DT2DPlot(ui.PlotWidget, self.colls)
        self.select_rect = SelectRect(ui.PlotWidget, app)
        ui.PlotWidget.scene().sigMouseClicked.connect(self.select_rect.mouse_click_slot)
        self.select_rect.select_OK.connect(print)
        self.dt2p.click_callbacks = [self.update_table]
        self.tdb.print_doings()
        self.tdb.print_need()
        self.ui.year.valueChanged.connect(lambda: self.change_year())
        self.ui.update_view.clicked.connect(lambda: self.update_view())

    def change_year(self):
        year = self.ui.year.value()
        self.rang.tm.setTime(datetime.time(0, 0, 0))
        self.rang.tM.setTime(datetime.time(23, 59, 59))
        self.rang.dm.setDate(datetime.date(year, 1, 1))
        self.rang.dM.setDate(datetime.date(year, 12, 31))
        self.update_view()

    def update_view(self):
        year = self.ui.year.value()
        where_dict = self.rang.get_sql_where_dict()
        plans = self.tdb.get_conds_plans(where_dict)
        ivtree = plans.get_ivtree(lambda p: Plan(p))
        self.dt2p.update_ivtree(ivtree, year)

    def update_table(self, t):
        select = list(map(lambda x: x.data, self.dt2p.item.ivtree[t.timestamp()]))
        print('found {} plans at {}'.format(len(select), t.strftime('%Y-%m-%d %H:%M:%S')))
        for p in select:
            print(p)
        print('')
        plans = Plans(select).str_datetime()
        self.table.setDataFrame(plans, 'tasks', column_set_cls=ColumnSetTasks, sql_table=self.tdb)


if __name__ == '__main__':
    app = QApplication([])
    win = QMainWindow()
    win.setWindowTitle('time-manager Date-Time 2D Image')
    dia = QDialog()
    dia.setWindowTitle('add task gen')
    ui = Ui_MainWindow()
    ui.setupUi(win)
    ud = Ui_Dialog()
    ud.setupUi(dia)
    win.show()
    Controller(ui, app)
    ui.add_task_gen.clicked.connect(dia.show)
    sys.exit(app.exec_())
