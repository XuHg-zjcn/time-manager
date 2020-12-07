#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QWidget
from PyQt5.QtCore import QRectF
from layout import Ui_MainWindow
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import sys


class dt2dplot:
    def __init__(self, pv, year):
        self.pv = pv
        self.d11 = datetime(year, 1, 1)
        dy1 = datetime(year+1, 1, 1)
        self.year = year
        self.days = (dy1-self.d11).days

        self.pv.invertY()
        self.set_xaixs()
        self.set_yaxis(6)

        arr = np.random.normal(0, 1, [self.days*288, 3])
        self.arr = np.cumsum(arr, axis=0)
        self.ii = pg.ImageItem(self.arr.reshape([-1, 288, 3]))
        self.ii.setRect(QRectF(0, 0, self.days, 24.0))
        self.pv.addItem(self.ii)

    def set_yaxis(self, n1=6, n2=24):
        """
        :n1: ticks with text
        :n2: all ticks
        n1<n2
        """
        if 24%n1 != 0 or 24%n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.pv.getAxis('left')
        t_text = [(i, str(i)) for i in range(0, 25, 24//n1)]
        t_no = [(i, '') for i in range(0, 25, 24//n2)]
        left.setTicks([t_text, t_no])
        left.setStyle(tickLength=5)  # Positive tick outside

    def set_xaixs(self):
        doys = []
        for y, m in [(self.year, i) for i in range(1, 13)]+[(self.year+1, 1)]:
            dx1 = datetime(y, m, 1)
            doy = (dx1-self.d11).days # day_of_year
            doys.append((doy, m))
        bottom = self.pv.getAxis('bottom')
        bottom.setTicks([[(x,m) for x,m in doys]])
        bottom.setStyle(tickLength=5)
        

    def update(self):
        print('event update')
        self.ii.setImage(self.arr.reshape([-1, 288, 3]))

    def __setitem__(self, time, color):
        ts0 = self.d11.timestamp()
        if isinstance(time, slice):
            b = (time.begin - ts0)/300
            e = (time.end - ts0)/300
            self.arr[b:e] = color
        else:
            t = (time - ts0)/300
            self.arr[t] = color

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    dt2p = dt2dplot(ui.PlotView, 2020)
    ui.lineEdit.returnPressed.connect(dt2p.update)
    MainWindow.show()
    sys.exit(app.exec_())