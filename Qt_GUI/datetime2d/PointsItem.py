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

    def setTimestampList(self, ts_lst, *args, **kwargs):
        pos = map(lambda ts: self.parent.time2xy(ts), ts_lst)
        super().setData(pos=pos, *args, **kwargs)

    def setTsLabel(self, ts_lst, labels,
                   hoverSymbol='+', hoverSize=10, hoverPen=None, hoverBrush=None,
                   *args, **kwargs):
        """
        悬停时显示标签
        """
        pos = map(lambda ts: self.parent.time2xy(ts), ts_lst)
        hover_color = QtGui.QColor(255, 127, 0)
        if hoverPen is None:
            hoverPen = hover_color
        if hoverBrush is None:
            hoverBrush = hover_color
        super().setData(pos=pos, data=labels, hoverable=True, tip=lambda x,y,data:data,
                        hoverSymbol='+', hoverSize=hoverSize,
                        hoverPen=hoverPen, hoverBrush=hoverBrush, *args, **kwargs)
