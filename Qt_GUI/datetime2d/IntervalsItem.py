import pyqtgraph as pg
from PyQt5 import QtCore, QtGui
from intervaltree import IntervalTree

from Qt_GUI.datetime2d import DT2DWidget
from my_libs.argb import ARGB


class DateTime2DItem(pg.GraphicsObject):
    def __init__(self, ivtree: IntervalTree, parent: DT2DWidget, default_color: int):
        """
        @param ivtree:
        iv.begin and iv.end are unix timestamp or datetime obj
        iv.data are my_libs.agrb.ARGB color

        @param parent: DT2DWidget obj
        """
        super().__init__()
        self.ivtree = ivtree
        self.parent = parent
        self.picture = QtGui.QPicture()
        if isinstance(default_color, int):
            default_color = ARGB.from_xrgb(default_color)
        self._draw_ivtree(default_color)

    def _draw_rect(self, p, doy, begin, end, color):
        """
        :para doy: int, day of year, 0-365, 0 is Jan 1
        :para begin: float 0-86400
        :para end: float 0-86400
        :para color: QColor
        """
        if begin == end:
            return
        assert 0 <= begin < end <= 24
        p.setPen(pg.mkPen(color))
        p.setBrush(pg.mkBrush(color))
        rect = QtCore.QRectF(doy+0.1, begin, 0.8, end-begin)
        p.drawRect(rect)

    def _draw_iv(self, p, begin, end, color):
        BEG = self.parent.time2xy(begin)
        END = self.parent.time2xy(end)
        color = QtGui.QColor.fromRgb(*color.RGBA())
        # filter date range into current year
        for doy in range(max(0, BEG[0]), min(END[0], self.parent.max_doy)+1):
            beg_sec = BEG[1] if doy == BEG[0] else 0
            end_sec = END[1] if doy == END[0] else 24
            self._draw_rect(p, doy, beg_sec, end_sec, color)

    def _draw_ivtree(self, default_color=None):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        for iv in sorted(self.ivtree):
            color = iv.data
            if color is None:
                color = default_color
            ovlps = self.ivtree[iv.begin]
            ovlps.remove(iv)
            if ovlps:
                first = min(ovlps, key=lambda x: x.end)
                color50 = color.copy()
                color50.A //= 2
                if first.begin == iv.begin and first.end <= iv.end:
                    self._draw_iv(p, iv.begin, iv.end, color)  # TODO: use mean color
                elif first.end < iv.end:
                    self._draw_iv(p, iv.begin, first.end, color50)
                    self._draw_iv(p, first.end, iv.end, color)
                else:
                    self._draw_iv(p, iv.begin, iv.end, color50)
            else:
                self._draw_iv(p, iv.begin, iv.end, color)
        p.end()
        print('draw_ivtree')

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
