#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QMainWindow, QWidget
from PyQt5.QtCore import QRectF
import pyqtgraph as pg
import numpy as np
from datetime import datetime


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

        self.arr = np.zeros([self.days*288, 3])
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.ii = pg.ImageItem(self.arr.reshape([-1, 288, 3]).transpose([1,0,2]))
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

    def update_show(self):
        print('update show')
        self.ii.setImage(self.arr.reshape([-1, 288, 3]).transpose([1,0,2]))

    def update_ivtree(self, ivtree, color=(255, 0, 0), clear=True):
        if clear is True:
            self.arr[:] = 0
        for iv in ivtree:
            sta = iv.begin
            end = iv.end
            self[sta:end] = color
        self.update_show()

    def __setitem__(self, time, color):
        ts0 = self.d11.timestamp()
        if isinstance(time, slice):
            s = (time.start - ts0)//300
            e = (time.stop - ts0)//300
            self.arr[int(s):int(e)] = color
        else:
            t = (time - ts0)//300
            self.arr[int(t)] = color
