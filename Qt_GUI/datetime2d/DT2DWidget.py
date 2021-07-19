from Qt_GUI.plotitems.PointsItem import PointsItem
from datetime import datetime, timedelta

import pyqtgraph as pg
from PyQt5.QtCore import Qt, pyqtSignal

from Qt_GUI.plotitems.IntervalsItem import DateTime2DItem


class vhLine:
    def __init__(self, pw):
        self.v = pg.InfiniteLine(angle=90, movable=False, )
        self.h = pg.InfiniteLine(angle=0, movable=False, )
        pw.addItem(self.v)
        pw.addItem(self.h)

    def set_xy(self, point):
        self.v.setPos(point.x())
        self.h.setPos(point.y())


class DT2DWidget(pg.PlotWidget):
    click = pyqtSignal(datetime)
    select_point = pyqtSignal(datetime)
    select_rect = pyqtSignal(datetime, datetime)

    def __init__(self, cw):
        super().__init__(cw)
        self._app = None
        self._swap = False       # swap XY axes
        self.last_select = None  # datetime obj, by last mouse click pos position
        self.items = None        # PlotItemTableWidget
        self.vh_line = vhLine(self)
        self.d11 = None
        self.max_doy = None      # leap year: 366
        self.invertY()           # original point in top-left corner
        self.set_YAxis(6)
        self.scene().sigMouseMoved.connect(self._mouse_move_slot)
        self.scene().sigMouseClicked.connect(self._mouse_click_slot)
        pg.setConfigOptions(imageAxisOrder='row-major')

    def build(self, app):
        self._app = app          # used for detect shift key

    def set_swap(self, new_state):
        """
        swap axes, and transpose
        @param new_state: bool, True for swap
        """
        self._swap = new_state
        self.set_XAxis()
        self.set_YAxis(6)
        self.set_XY_full_range()

    def addItem2(self, item):
        if self._swap:
            item.rotate(90)
            item.scale(1, -1)
        self.addItem(item)

    def set_year(self, year=None):
        """
        clear all items in the Widget, set XAxis with leap year.
        @param year: 0-9999, default is current year.
        """
        if year is None:
            year = datetime.today().year
        self.d11 = datetime(year, 1, 1)
        self.max_doy = (datetime(year+1, 1, 1) - self.d11).days
        self.set_XAxis(year)

    def time2xy(self, ts):
        if isinstance(ts, float) or isinstance(ts, int):
            ts = datetime.fromtimestamp(ts)
        dt = ts - self.d11
        x = dt.days
        if x >= self.max_doy:
            return self.max_doy-1, 24
        else:
            y = (dt.seconds + dt.microseconds/1e6)/3600
            return x, y

    def xy2time(self, x:int, y:float):
        # TODO: TypeError: unsupported operand type(s) for +:
        #  'NoneType' and 'datetime.timedelta'
        return self.d11 + timedelta(days=x, hours=y)

    def set_YAxis(self, n1=6, n2=24):
        """
        @param n1: ticks with text
        @param n2: all ticks
        n1<n2
        """
        if 24 % n1 != 0 or 24 % n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.getAxis('bottom' if self._swap else 'left')
        t_text = [(i, str(i)) for i in range(0, 25, 24//n1)]
        t_no = [(i, '') for i in range(0, 25, 24//n2)]
        left.setTicks([t_text, t_no])
        left.setStyle(tickLength=5)  # Positive tick outside

    def set_XAxis(self, year=None):
        """set XAxis with leap year."""
        if year is None:
            year = self.d11.year
        doys = []
        for y, m in [(year, i) for i in range(1, 13)]+[(year+1, 1)]:
            dx1 = datetime(y, m, 1)
            doy = (dx1 - self.d11).days  # day_of_year
            doys.append((doy, m))
        bottom = self.getAxis('left' if self._swap else 'bottom')
        bottom.setTicks([[(x, m) for x, m in doys]])
        bottom.setStyle(tickLength=5)

    def set_XY_full_range(self):
        """set XAxis and YAxis to full range, with axes swap state."""
        self.setXRange(0, 24 if self._swap else 366)
        self.setYRange(0, 366 if self._swap else 24)

    def _mouse_move_slot(self, pos):
        if self.sceneBoundingRect().contains(pos):
            point = self.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
            self.vh_line.set_xy(point)

    def _mouse_click_slot(self, event):
        pos = event._scenePos
        modifiers = self._app.keyboardModifiers()
        point = self.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
        x, y = point.x(), point.y()
        if self._swap:
            y, x = x, y
        dati = self.xy2time(int(x), y)
        self.click.emit(dati)
        if modifiers == Qt.ShiftModifier and self.last_select is not None:
            self.select_rect.emit(self.last_select, dati)
        else:
            self.last_select = dati
            self.select_point.emit(dati)
