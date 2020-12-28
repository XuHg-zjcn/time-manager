from collections import namedtuple
from datetime import datetime
from PyQt5.QtGui import QPainterPath, QFont, QTransform
from sklearn.cluster import MeanShift
from threading import Thread
import pyqtgraph as pg


TextSymbol = namedtuple("TextSymbol", "label symbol scale")

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
        ts = (lambda x:(x.sta_time + x.end_time)/2)(pobj.p_time)
        xy = self.time2xy(ts)
        super().append(xy)


class Cluster:
    def __init__(self, ivtree, d11, db, scatter, day_div=5):
        self.ivtree = ivtree
        self.d11 = d11
        self.db = db
        self.day_div = day_div
        self.dbt2plst = {}
        self.dbt2text = {}
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
            if iv.data.dbtype not in self.dbt2plst:
                self.dbt2plst[iv.data.dbtype] = PlanList(self.d11, self.day_div)
            self.dbt2plst[iv.data.dbtype].append(iv.data)
        for dbtype in self.dbt2plst.keys():
            dbt = self.db.find_dbtype(dbtype)
            self.dbt2text[dbtype] = dbt.name if dbt is not None else 'dbtype{}'.format(dbtype)

    def thread(self, scatter):
        print('thread')
        spots = []
        for dbtype, plst in self.dbt2plst.items():
            text = self.dbt2text[dbtype]
            ms = MeanShift(bandwidth=5)
            ms.fit(plst)
            centers = ms.cluster_centers_
            centers[:,0] *= self.day_div
            for c in centers:
                label = self.create_label(text, 0)
                spots.append({'pos': c, 'data': 1, 'symbol': label.symbol, 'size': label.scale*10})
        scatter.setData(spots)
