from collections import namedtuple
from datetime import datetime
from threading import Thread

from PyQt5.QtGui import QPainterPath, QFont, QTransform, QColor
from sklearn.cluster import MeanShift

from my_libs.argb import ARGB


TextSymbol = namedtuple("TextSymbol", "label symbol scale")
TxtClr = namedtuple("TxtClr", "text color")


class PlanList(list):
    def __init__(self, d11, day_div=5):
        self.d11 = d11
        self.day_div = day_div
        super().__init__()

    def time2xy(self, time):
        if isinstance(time, float) or isinstance(time, int):
            time = datetime.fromtimestamp(time)
        dt = time - self.d11
        days = dt.days/self.day_div
        hours = (dt.seconds + dt.microseconds/1e6)/3600
        return days, hours

    def append(self, pobj):
        """
        :para pobj: Plan obj
        """
        ts = (pobj['sta'] + pobj['end']) / 2
        xy = self.time2xy(ts)
        super().append(xy)


class Cluster:
    def __init__(self, ivtree, d11, scatter, day_div=5,
                 func_classify=lambda p: 0,
                 func_textcolor=lambda x: TxtClr('name', ARGB(0, 255, 255))):
        self.ivtree = ivtree
        self.d11 = d11
        self.day_div = day_div
        self.func_classify = func_classify
        self.func_textcolor = func_textcolor
        self.dbt2plst = {}
        self.dbt2dbtp = {}
        self.before()
        thr = Thread(target=self.thread, args=(scatter,))
        thr.start()

    @staticmethod
    def create_label(label, angle):
        symbol = QPainterPath()
        f = QFont()
        f.setPointSize(10)
        symbol.addText(0, 0, f, label)
        br = symbol.boundingRect()
        scale = min(1. / br.width(), 1. / br.height())
        tr = QTransform()
        tr.scale(scale, scale)
        tr.rotate(angle)
        tr.translate(-br.x() - br.width() / 2., -br.y() - br.height() / 2.)
        return TextSymbol(label, tr.map(symbol), 0.1 / scale)

    def before(self):
        for iv in self.ivtree:
            ctg = self.func_classify(iv.data)  # category
            if ctg not in self.dbt2plst:
                self.dbt2plst[ctg] = PlanList(self.d11, self.day_div)
            self.dbt2plst[ctg].append(iv.data)
        for ctg in self.dbt2plst.keys():
            txt_clr = self.func_textcolor(ctg)
            self.dbt2dbtp[ctg] = txt_clr

    def thread(self, scatter):
        print('thread')
        spots = []
        for dbtype, plst in self.dbt2plst.items():
            tp = self.dbt2dbtp[dbtype]
            inv_color = QColor(*tp.color.RGB())
            ms = MeanShift(bandwidth=5)
            ms.fit(plst)
            centers = ms.cluster_centers_
            centers[:,0] *= self.day_div
            for c in centers:
                pos = c
                pos[0] += 0.5
                label = self.create_label(tp.text, 0)
                spots.append({'pos': pos, 'data': 1, 'pen':inv_color, 'brush': inv_color,
                              'symbol': label.symbol, 'size': label.scale*10})
        scatter.setData(spots)
