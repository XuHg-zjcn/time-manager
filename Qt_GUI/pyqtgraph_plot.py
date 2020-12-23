from datetime import datetime
import pyqtgraph as pg
from .plot2d import DateTime2DItem


class dt2dplot:
    def __init__(self, pv):
        self.pv = pv
        self.item = DateTime2DItem()

        self.pv.addItem(self.item)
        self.pv.invertY()
        self.set_yaxis(6)
        pg.setConfigOptions(imageAxisOrder='row-major')

    def set_yaxis(self, n1=6, n2=24):
        """
        :n1: ticks with text
        :n2: all ticks
        n1<n2
        """
        if 24 % n1 != 0 or 24 % n2 != 0:
            raise ValueError("n can't div by 24")
        left = self.pv.getAxis('left')
        t_text = [(i, str(i)) for i in range(0, 25, 24//n1)]
        t_no = [(i, '') for i in range(0, 25, 24//n2)]
        left.setTicks([t_text, t_no])
        left.setStyle(tickLength=5)  # Positive tick outside

    def set_xaixs(self):
        doys = []
        for y, m in [(self.year, i) for i in range(1, 13)]+[(self.year+1, 1)]:
            dx1 = datetime(y, m, 1)
            doy = (dx1 - self.item.d11).days  # day_of_year
            doys.append((doy, m))
        bottom = self.pv.getAxis('bottom')
        bottom.setTicks([[(x, m) for x, m in doys]])
        bottom.setStyle(tickLength=5)

    def update_ivtree(self, ivtree, year):
        self.year = year
        self.item.draw_ivtree(ivtree, year)
        self.set_xaixs()
