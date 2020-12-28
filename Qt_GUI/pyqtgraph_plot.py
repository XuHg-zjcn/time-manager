from datetime import datetime
import pyqtgraph as pg
from .plot2d import DateTime2DItem
from .cluster import Cluster


class dt2dplot:
    def __init__(self, pw, db):
        self.pw = pw
        self.db = db
        self.item = DateTime2DItem()
        self.scatter = pg.ScatterPlotItem()
        self.pw.addItem(self.item)
        self.pw.addItem(self.scatter)
        self.vLine = pg.InfiniteLine(angle=90, movable=False, )
        self.hLine = pg.InfiniteLine(angle=0, movable=False, )
        self.pw.addItem(self.vLine)
        self.pw.addItem(self.hLine)
        self.pw.invertY()
        self.set_yaxis(6)
        self.pw.scene().sigMouseMoved.connect(self.mouse_move_slot)
        self.pw.scene().sigMouseClicked.connect(self.mouse_click_slot)
        pg.setConfigOptions(imageAxisOrder='row-major')

    def set_yaxis(self, n1=6, n2=24):
        """
        :n1: ticks with text
        :n2: all ticks
        n1<n2
        """
        if 24 % n1 != 0 or 24 % n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.pw.getAxis('left')
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
        bottom = self.pw.getAxis('bottom')
        bottom.setTicks([[(x, m) for x, m in doys]])
        bottom.setStyle(tickLength=5)

    def update_ivtree(self, ivtree, year):
        self.item.draw_ivtree(ivtree, year)
        self.set_xaixs(year)
        Cluster(ivtree, self.item.d11, self.db, self.scatter)

    def mouse_move_slot(self, pos):
        if self.pw.sceneBoundingRect().contains(pos):
            point = self.pw.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
            self.vLine.setPos(point.x())
            self.hLine.setPos(point.y())

    def mouse_click_slot(self, event):
        pos = event._scenePos
        if self.pw.sceneBoundingRect().contains(pos):
            point = self.pw.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
            doy = int(point.x())
            sec = point.y()*3600
            t = self.item.xy2time(doy, sec).timestamp()
            print(self.item.ivtree[t])
        pass
