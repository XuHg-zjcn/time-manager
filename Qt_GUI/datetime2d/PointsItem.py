import pyqtgraph as pg
import pandas as pd
from PyQt5 import QtGui

from Qt_GUI.datetime2d import DT2DWidget


class PointsItem(pg.ScatterPlotItem):
    def __init__(self, parent: DT2DWidget, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)

    def setDataFrame(self, data: pd.DataFrame):
        pos = []
        for ts in data['timestamp']:
            xy = self.parent.time2xy(ts)
            pos.append(xy)
        if 'color' in data:
            color = map(lambda clr: QtGui.QColor.fromRgb(clr), data['color'])
        else:
            color = QtGui.QColor.fromRgb(0x00ffff)
        super().setData(pos=pos, pen=color, brush=color)

    def setTimestampList(self, data, *args, **kwargs):
        pos = map(lambda ts: self.parent.time2xy(ts), data)
        super().setData(pos=pos, args=args, kwargs=kwargs)
