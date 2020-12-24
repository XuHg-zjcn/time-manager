from datetime import datetime
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui


class DateTime2DItem(pg.GraphicsObject):
    def __init__(self, ivtree=None, year=None):
        self.ivtree = ivtree
        self.year = year
        self.picture = QtGui.QPicture()
        if ivtree is not None and year is not None:
            self.draw_ivtree(ivtree, year)
        else:
            self.d11 = None
            self.max_doy = None
        super().__init__()

    def _draw_rect(self, p, doy, begin, end, color):
        """
        :para doy: int, day of year, 0-365, 0 is Jan 1
        :para begin: float 0-86400
        :para end: float 0-86400
        :para color: QColor
        """
        assert 0 <= begin < end < 86400
        begin /= 3600
        end /= 3600
        p.setPen(pg.mkPen(color))
        p.setBrush(pg.mkBrush(color))
        rect = QtCore.QRectF(doy, begin, 0.8, end-begin)
        p.drawRect(rect)

    def _draw_iv(self, p, iv):
        BEG = datetime.fromtimestamp(iv.begin) - self.d11
        END = datetime.fromtimestamp(iv.end) - self.d11
        color = QtGui.QColor.fromRgb(*iv.data.color.RGBA())
        for doy in range(max(0, BEG.days), min(END.days, self.max_doy)+1):
            beg_sec = BEG.seconds if doy == BEG.days else 0
            end_sec = END.seconds if doy == END.days else 86399
            self._draw_rect(p, doy, beg_sec, end_sec, color)

    def draw_ivtree(self, ivtree, year):
        self.ivtree = ivtree
        self.year = year
        self.picture = QtGui.QPicture()
        self.d11 = datetime(year, 1, 1)
        self.max_doy = (datetime(year+1, 1, 1) - self.d11).days
        p = QtGui.QPainter(self.picture)
        for iv in ivtree:
            self._draw_iv(p, iv)
        p.end()
        print('draw_ivtree')

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
