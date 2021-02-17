from datetime import datetime
import pyqtgraph as pg
from PyQt5.QtCore import Qt, pyqtSignal

from .Item import DateTime2DItem
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

    def build(self, app, colls):
        self.app = app
        self.colls = colls
        self.last_select = None
        self.item = None
        self.scatter = pg.ScatterPlotItem()
        self.scatter.setZValue(10)
        self.addItem(self.scatter)
        self.vh_line = vhLine(self)
        self.invertY()
        self.set_yaxis(6)
        self.scene().sigMouseMoved.connect(self.mouse_move_slot)
        self.scene().sigMouseClicked.connect(self.mouse_click_slot)
        pg.setConfigOptions(imageAxisOrder='row-major')

    def set_yaxis(self, n1=6, n2=24):
        """
        :n1: ticks with text
        :n2: all ticks
        n1<n2
        """
        if 24 % n1 != 0 or 24 % n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.getAxis('left')
        t_text = [(i, str(i)) for i in range(0, 25, 24//n1)]
        t_no = [(i, '') for i in range(0, 25, 24//n2)]
        left.setTicks([t_text, t_no])
        left.setStyle(tickLength=5)  # Positive tick outside

    def set_xaixs(self, year):
        doys = []
        for y, m in [(year, i) for i in range(1, 13)]+[(year+1, 1)]:
            dx1 = datetime(y, m, 1)
            doy = (dx1 - self.item.d11).days  # day_of_year
            doys.append((doy, m))
        bottom = self.getAxis('bottom')
        bottom.setTicks([[(x, m) for x, m in doys]])
        bottom.setStyle(tickLength=5)

    def set_xy_full_range(self):
        self.setXRange(0, 366)
        self.setYRange(0, 24)

    def update_ivtree(self, ivtree, year):
        ivt_color = ivtree.map_data(lambda p: p.get_collect_color(self.colls))
        self.ivtree = ivtree
        self.removeItem(self.item)
        self.item = DateTime2DItem(ivt_color, year)
        self.item.setZValue(0)
        self.addItem(self.item)
        self.set_xaixs(year)
        self.set_xy_full_range()

    def start_cluster(self):
        if not hasattr(self, 'ivtree'):
            raise RuntimeError('start_cluster before update_ivtree')
        clu = Cluster(self.ivtree, self.item.d11, self.scatter,
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
        doy = int(point.x())
        sec = point.y()*3600
        dati = self.item.xy2time(doy, sec)
        self.click.emit(dati)
        if modifiers == Qt.ShiftModifier and self.last_select is not None:
            self.select_rect.emit(self.last_select, dati)
        else:
            self.last_select = dati
            self.select_point.emit(dati)
