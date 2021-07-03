import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QDateEdit, QTimeEdit, QComboBox

from my_libs.datetime_utils import date2ts0, time2float


class DateTimeRange(QWidget):
    change = pyqtSignal()
    settings = ['2D包含',  # a< Ds<De <b && {(c< Ts<Te <d) if (Ds==De) else (c=0,d=24)}
                '2D重叠',  # (Ts<=d && c<=Te) if Ds==De, else omitted
                '1D包含',  # (a,c) <= sta <= end <= (b,d)'
                '1D重叠',  # [(a,c), (b,d)] overlaps [sta, end]
                '点选择']  # sta < (a,c) < end

    def __init__(self, dm: QDateEdit, dM: QDateEdit,
                       tm: QTimeEdit, tM: QTimeEdit,
                       comb: QComboBox):
        super().__init__()
        self.dm = dm
        self.dM = dM
        self.tm = tm
        self.tM = tM
        self.comb = comb
        dm.dateChanged.connect(self.change.emit)
        dM.dateChanged.connect(self.change.emit)
        tm.timeChanged.connect(self.change.emit)
        tM.timeChanged.connect(self.change.emit)
        comb.currentIndexChanged.connect(self.change.emit)
        self.comb.clear()
        self.comb.addItems(self.settings)
        self.comb.currentIndexChanged.connect(self.comb_slot)
        self.default4dt_comb_index = 0

    def comb_slot(self, index):
        is_enable = index != 4
        self.dM.setEnabled(is_enable)
        self.tM.setEnabled(is_enable)
        if is_enable:
            self.default4dt_comb_index = index

    def get4py(self):
        dm_ = self.dm.date().toPyDate()
        dM_ = self.dM.date().toPyDate()
        tm_ = self.tm.time().toPyTime()
        tM_ = self.tM.time().toPyTime()
        return dm_, dM_, tm_, tM_

    def get2py(self):
        dm, dM, tm, tM = self.get4py()
        m = datetime.datetime.combine(dm, tm)
        M = datetime.datetime.combine(dM, tM)
        return m, M

    def get2float(self):
        m, M = self.get2py()
        return m.timestamp(), M.timestamp()

    def get4float(self):
        dm, dM, tm, tM = self.get4py()
        dmf = date2ts0(dm)
        dMf = date2ts0(dM)
        tmf = time2float(tm)
        tMf = time2float(tM)
        return dmf, dMf, tmf, tMf

    def get4str(self):
        dm_ = self.dm.date().toString('yyyy-MM-dd')
        dM_ = self.dM.date().toString('yyyy-MM-dd')
        tm_ = self.tm.time().toString('hh:mm:ss')
        tM_ = self.tM.time().toString('hh:mm:ss')
        return dm_, dM_, tm_, tM_

    def set2datetime(self, m, M):
        d1 = m.date()
        d2 = M.date()
        t1 = m.time()
        t2 = M.time()
        self.dm.setDate(min(d1, d2))
        self.dM.setDate(max(d1, d2))
        self.tm.setTime(min(t1, t2))
        self.tM.setTime(max(t1, t2))
        if self.comb.currentIndex() == 4:
            self.comb.setCurrentIndex(self.default4dt_comb_index)

    def set1datetime(self, m):
        self.comb.setCurrentIndex(4)
        self.dm.setDate(m.date())
        self.tm.setTime(m.time())

    def set_year0101_1231(self, year):
        d0101 = datetime.datetime(year, 1,  1,  0,  0,  0)
        d1231 = datetime.datetime(year, 12, 31, 23, 59, 59)
        self.set2datetime(d0101, d1231)

    def get_sql_where_dict(self):
        # TODO: timezone
        name = self.comb.currentText()
        dm, dM, tm, tM = self.get4str()
        m, M = self.get2float()
        if name == '2D包含':
            if tm == '00:00:00' and tM == '23:59:59':
                ret = {'sta': ('>=', m), 'end': ('<=', M)}  # same to '1D包含'
            else:
                dmf, dMf, tmf, tMf = self.get4float()
                ret = {'sta': ('>=', dmf),
                       'end': ('<=', dMf),
                       '(sta+8*3600)%86400': ('>=', tmf),
                       '(end+8*3600)%86400': ('<=', tMf),
                       'CAST((end+8*3600)/86400 as int)=CAST((sta+8*3600)/86400 as int)': []}
        elif name == '2D重叠':
            dmf, dMf, tmf, tMf = self.get4float()
            w_str = ('sta>=? AND end<? AND (sta+8*3600)%86400<? AND (end+8*3600)%86400>? OR '
                     # date of end != date of start
                     '((sta+8*3600)%86400<=? AND sta>=? AND sta<? OR '
                     '(end+8*3600)%86400>? AND end>=? AND end<?) AND '
                     'CAST((end+8*3600)/86400 as int)!=CAST((sta+8*3600)/86400 as int) OR '
                     # date of end > date of start + 1
                     'end>=?+86400 AND sta<?-86400 AND '
                     'CAST((end+8*3600)/86400 as int)>CAST((sta+8*3600)/86400 as int)+1')
            w_paras = [dmf, dMf, tMf, tmf, tMf, dmf, dMf, tmf, dmf, dMf, dmf, dMf]
            ret = {w_str: w_paras}
        elif name == '1D包含':
            ret = {'sta': ('>=', m), 'end': ('<=', M)}
        elif name == '1D重叠':
            ret = {'sta': ('<=', M), 'end': ('>=', m)}
        elif name == '点选择':
            ret = {'sta': ('<=', m), 'end': ('>=', m)}
        else:
            raise ValueError('ComboBox get unknown name')
        return ret
