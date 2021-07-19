import pyqtgraph as pg
import pandas as pd
from PyQt5 import QtGui


class PointsItem(pg.ScatterPlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ts_lst = []
        self.labels = None

    def setTimestampList(self, ts_lst):
        self.ts_lst = ts_lst

    def setHover(self, hoverable=True, tip=None,
                 hoverSymbol='+', hoverSize=10, hoverPen=None, hoverBrush=None):
        hover_color = QtGui.QColor(255, 127, 0)
        hoverPen = hoverPen or hover_color
        hoverBrush = hoverBrush or hover_color
        self.setData(hoverable=True, tip=tip,
                     hoverSymbol='+', hoverSize=hoverSize,
                     hoverPen=hoverPen, hoverBrush=hoverBrush)

    def setTsLabel(self, ts_lst, labels, *args, **kwargs):
        """
        悬停时显示标签
        """
        self.setTimestampList(ts_lst, *args, **kwargs)
        self.labels = labels
        self.setHover(tip=lambda x,y,data:data)

    def update_xy(self, time2xy):
        pos = map(lambda ts: time2xy(ts), self.ts_lst)
        super().setData(pos=pos, data=self.labels)