#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:53:35 2020

@author: xrj
"""
import sys
from datetime import datetime

from Qt_GUI.add_task_gen import Ui_Dialog

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from Qt_GUI.layout import Ui_MainWindow
from Qt_GUI.pyqtgraph_plot import DT2DPlot, SelectRect
from commd_line.init_config import conn
from sqlite_api.tables import CollTable
from sqlite_api.task_db import TaskTable, Plan, Plans, ColumnSetTasks
from my_libs.smart_strptime.my_datetime import sTimeRange


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


class Controller:
    """
    select data and display.
    """

    def __init__(self, ui, app):
        self.ui = ui
        self.start = QTimeRange(self.ui.min_sta, self.ui.max_sta)
        self.stop = QTimeRange(self.ui.min_end, self.ui.max_end)
        # set current year
        year = datetime.now().year
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
        tR = sTimeRange.M(year)
        self.start.setRange(tR)
        self.stop.setRange(tR)
        self.update_view()

    def update_view(self):
        year = self.ui.year.value()
        start = self.start.timestamp_tuple()
        stop = self.stop.timestamp_tuple()
        plans = self.tdb.get_conds_plans({'sta': start, 'end': stop})
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
