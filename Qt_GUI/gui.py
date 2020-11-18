#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 04:55:45 2020

@author: xrj
"""
from datetime import datetime
import math
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg

pg.setConfigOptions(imageAxisOrder='row-major')
app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('time-manager Date-Time 2D Image')

y20 = datetime(2020, 1, 1).timestamp()
y21 = datetime(2021, 1, 1).timestamp()
olen = int((y21-y20)/(60*5))
def update(ivtree):
    img = np.zeros(olen)
    for iv in ivtree:
        sta = iv.begin
        end = iv.end
        sta_5m = int((sta-y20)/(60*5))
        end_5m = int((end-y20)/(60*5))
        img[sta_5m:end_5m] = math.log(end-sta+1)
    img = img.reshape(-1, 24*60//5).transpose()
    imv.setImage(img, scale=(2, 1))
    QtGui.QApplication.instance().exec_()
