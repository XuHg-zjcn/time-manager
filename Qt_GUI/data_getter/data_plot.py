from intervaltree import IntervalTree
from my_libs.sqltable import SqlTable
from Qt_GUI.datetime2d.DT2DWidget import DT2DWidget


class DataPlot:
    def __init__(self, db:SqlTable, dt2d:DT2DWidget, name:str=None):
        self._db = db
        self._dt2d = dt2d
        self._color = 0xffff00
        self._name = name

    def update(self, where_dict, color=None):
        df = self._db.get_conds_execute(where_dict, ['sta', 'end'])
        ivt = IntervalTree.from_tuples(df)
        if color is not None:
            self._color =color
        self._dt2d.draw_ivtree(ivt, default_color=self._color, name=self._name)
