from datetime import datetime, timedelta
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui


class DateTime2DItem(pg.GraphicsObject):
    def __init__(self, func_color):
        self.ivtree = None
        self.year = None
        self.picture = QtGui.QPicture()
        self.d11 = None
        self.max_doy = None
        self.func_color = func_color
        super().__init__()

    def time2xy(self, time):
        if isinstance(time, float) or isinstance(time, int):
            time = datetime.fromtimestamp(time)
        dt = time - self.d11
        return dt.days, dt.seconds + dt.microseconds/1e6

    def xy2time(self, x:int, y:float):
        # TODO: TypeError: unsupported operand type(s) for +: 'NoneType' and 'datetime.timedelta'
        return self.d11 + timedelta(days=x, seconds=y)

    def _draw_rect(self, p, doy, begin, end, color):
        """
        :para doy: int, day of year, 0-365, 0 is Jan 1
        :para begin: float 0-86400
        :para end: float 0-86400
        :para color: QColor
        """
        if begin == end:
            return
        assert 0 <= begin < end < 86400
        begin /= 3600
        end /= 3600
        p.setPen(pg.mkPen(color))
        p.setBrush(pg.mkBrush(color))
        rect = QtCore.QRectF(doy+0.1, begin, 0.8, end-begin)
        p.drawRect(rect)

    def _draw_iv(self, p, begin, end, color):
        BEG = self.time2xy(begin)
        END = self.time2xy(end)
        color = QtGui.QColor.fromRgb(*color.RGBA())
        for doy in range(max(0, BEG[0]), min(END[0], self.max_doy)+1):
            beg_sec = BEG[1] if doy == BEG[0] else 0
            end_sec = END[1] if doy == END[0] else 86399
            self._draw_rect(p, doy, beg_sec, end_sec, color)

    def draw_ivtree(self, ivtree, year):
        self.ivtree = ivtree
        self.year = year
        self.picture = QtGui.QPicture()
        self.d11 = datetime(year, 1, 1)
        self.max_doy = (datetime(year+1, 1, 1) - self.d11).days
        p = QtGui.QPainter(self.picture)
        for iv in sorted(ivtree):
            color = self.func_color(iv.data)
            ovlps = ivtree[iv.begin]
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
