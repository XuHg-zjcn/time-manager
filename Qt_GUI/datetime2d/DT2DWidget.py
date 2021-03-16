from datetime import datetime, timedelta

import pyqtgraph as pg
from PyQt5.QtCore import Qt, pyqtSignal

from sqlite_api.task_db import Plans, Plan
from .IntervalsItem import DateTime2DItem
from ..cluster import Cluster


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

    def __init__(self, parent):
        super().__init__(parent)
        self._swap = False
        self.plans = None
        self.last_select = None
        self.items = {}
        self.scatter = pg.ScatterPlotItem()
        self.scatter.setZValue(10)
        self.addItem2(self.scatter)
        self.vh_line = vhLine(self)
        self.invertY()
        self.set_yaxis(6)
        self.scene().sigMouseMoved.connect(self.mouse_move_slot)
        self.scene().sigMouseClicked.connect(self.mouse_click_slot)
        pg.setConfigOptions(imageAxisOrder='row-major')
        self.set_year(datetime.today().year)

    def build(self, app, colls):
        self.app = app      # don't move this codes
        self.colls = colls  # to __init__, it call in pyuic5 generated code

    def set_swap(self, new_state):
        self._swap = new_state
        # TODO: swap xy for scatter texts
        for item in self.items.values():
            item.rotate(90)
            item.scale(1, -1)
        self.set_xaixs()
        self.set_yaxis(6)
        self.set_xy_full_range()

    def addItem2(self, item):
        if self._swap:
            item.rotate(90)
            item.scale(1, -1)
        self.addItem(item)

    def set_year(self, year):
        self.clear_plans()
        self.d11 = datetime(year, 1, 1)
        self.max_doy = (datetime(year+1, 1, 1) - self.d11).days
        self.set_xaixs(year)

    def time2xy(self, ts):
        if isinstance(ts, float) or isinstance(ts, int):
            ts = datetime.fromtimestamp(ts)
        dt = ts - self.d11
        return dt.days, (dt.seconds + dt.microseconds/1e6)/3600

    def xy2time(self, x:int, y:float):
        # TODO: TypeError: unsupported operand type(s) for +:
        #  'NoneType' and 'datetime.timedelta'
        return self.d11 + timedelta(days=x, hours=y)

    def set_yaxis(self, n1=6, n2=24):
        """
        :n1: ticks with text
        :n2: all ticks
        n1<n2
        """
        if 24 % n1 != 0 or 24 % n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.getAxis('bottom' if self._swap else 'left')
        t_text = [(i, str(i)) for i in range(0, 25, 24//n1)]
        t_no = [(i, '') for i in range(0, 25, 24//n2)]
        left.setTicks([t_text, t_no])
        left.setStyle(tickLength=5)  # Positive tick outside

    def set_xaixs(self, year=None):
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

    def set_xy_full_range(self):
        self.setXRange(0, 24 if self._swap else 366)
        self.setYRange(0, 366 if self._swap else 24)

    def draw_plans(self, plans: Plans, year=None, name=None, z=0):
        """
        draw plans datetime2d.
        @param plans: Plans(pd.DataFrame) object
        @param year: optional, see `set_year`
        @param name: optional, None will default item
        @param z: ZValue(layer) of pyqtgraph PlotItem
        @return: None
        """
        if name is None:
            self.plans = plans
        ivt_color = plans.get_ivtree(lambda p: Plan(p).get_collect_color(self.colls))
        self.draw_ivtree(ivt_color, year=year, name=name, z=z)

    def draw_ivtree(self, ivt_color, default_color=0x00ffff, year=None, name=None, z=0):
        if name in self.items:  # name normal is None or string
            self.remove_plans(name)
        if year is not None:
            self.set_year(year)
        item_new = DateTime2DItem(ivt_color, self, default_color)
        item_new.setZValue(z)
        self.items[name] = item_new
        self.addItem2(item_new)
        self.set_xy_full_range()

    def remove_plans(self, name):
        """
        remove showing plans.
        """
        print('remove dt2d', name)
        self.removeItem(self.items.pop(name))

    def clear_plans(self):
        for name in self.items:
            self.removeItem(self.items[name])

    def start_cluster(self):
        if self.plans is None:
            raise RuntimeError('start_cluster before update_ivtree')
        clu = Cluster(self.plans, self.d11, self.scatter,
                      func_classify=lambda p: p['rec_id'],
                      func_textcolor=self.colls.find_txtclr)
        clu.start()

    def mouse_move_slot(self, pos):
        if self.sceneBoundingRect().contains(pos):
            point = self.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
            self.vh_line.set_xy(point)

    def mouse_click_slot(self, event):
        pos = event._scenePos
        modifiers = self.app.keyboardModifiers()
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
