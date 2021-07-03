import datetime

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from my_libs.datetime_utils import date2ts0, time2float
from Qt_GUI.selector import Ui_Selector


class Selector2(Ui_Selector, QtWidgets.QWidget):
    change = QtCore.pyqtSignal()
    settings = ['2D包含',  # a< Ds<De <b && {(c< Ts<Te <d) if (Ds==De) else (c=0,d=24)}
                '2D重叠',  # (Ts<=d && c<=Te) if Ds==De, else omitted
                '1D包含',  # (a,c) <= sta <= end <= (b,d)'
                '1D重叠',  # [(a,c), (b,d)] overlaps [sta, end]
                '点选择']  # sta < (a,c) < end

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        Ui_Selector.__init__(self)

    def build(self):
        self.date_min.dateChanged.connect(self.change.emit)
        self.date_max.dateChanged.connect(self.change.emit)
        self.time_min.timeChanged.connect(self.change.emit)
        self.time_max.timeChanged.connect(self.change.emit)
        self.x_setting.currentIndexChanged.connect(self.change.emit)
        self.x_setting.clear()
        self.x_setting.addItems(self.settings)
        self.x_setting.currentIndexChanged.connect(self.comb_slot)
        self.default4dt_comb_index = 0

    def comb_slot(self, index):
        is_enable = index != 4
        self.date_max.setEnabled(is_enable)
        self.time_max.setEnabled(is_enable)
        if is_enable:
            self.default4dt_comb_index = index

    def get4py(self):
        dm_ = self.date_min.date().toPyDate()
        dM_ = self.date_max.date().toPyDate()
        tm_ = self.time_min.time().toPyTime()
        tM_ = self.time_max.time().toPyTime()
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
        dm_ = self.date_min.date().toString('yyyy-MM-dd')
        dM_ = self.date_max.date().toString('yyyy-MM-dd')
        tm_ = self.time_min.time().toString('hh:mm:ss')
        tM_ = self.time_max.time().toString('hh:mm:ss')
        return dm_, dM_, tm_, tM_

    def set2datetime(self, m, M):
        d1 = m.date()
        d2 = M.date()
        t1 = m.time()
        t2 = M.time()
        self.date_min.setDate(min(d1, d2))
        self.date_max.setDate(max(d1, d2))
        self.time_min.setTime(min(t1, t2))
        self.time_max.setTime(max(t1, t2))
        if self.x_setting.currentIndex() == 4:
            self.x_setting.setCurrentIndex(self.default4dt_comb_index)

    def set1datetime(self, m):
        self.x_setting.setCurrentIndex(4)
        self.date_min.setDate(m.date())
        self.time_min.setTime(m.time())

    def set_year0101_1231(self, year):
        d0101 = datetime.datetime(year, 1,  1,  0,  0,  0)
        d1231 = datetime.datetime(year, 12, 31, 23, 59, 59)
        self.set2datetime(d0101, d1231)

    def get_sql_where_dict(self):
        # TODO: timezone
        name = self.x_setting.currentText()
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
