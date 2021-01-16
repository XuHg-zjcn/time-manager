import time
from pickle import dumps

from Qt_GUI.cluster import TxtClr
from sqlite_api.argb import ARGB
from sqlite_api.task_db import SqlTable


class CollTable(SqlTable):
    name2dtype = [('name', 'TEXT'), ('enable', 'BOOL'), ('dump', 'BLOB'),
                  ('runs', 'INT'), ('items', 'INT'),
                  ('t_max', 'REAL'), ('t_last', 'REAL'), ('color', 'INT')]
    table_name = 'collectors'

    def add_item(self, coll_obj, enable=True, color=0xffffff00, commit=True):
        if isinstance(color, int):
            pass
        elif isinstance(color, ARGB):
            color = color.ARGBi()
        else:
            raise TypeError('unsupported color type:', type(color))
        self.insert([coll_obj.coll_name, enable, dumps(coll_obj),
                     0, 0, 0, time.time(), color], commit)

    def find_txtclr(self, cid):
        txt, clr = self.get_conds_onlyone({'id': cid}, ['name', 'color'],
                                          ['{}'.format(cid), 0xff00ffff])
        clr = ARGB.from_argb(clr).inv_bin()
        return TxtClr(txt, clr)


class CollLogTable(SqlTable):
    name2dtype = [('cid', 'INT'), ('run_i', 'INT'), ('run_time', 'DATETIME'),
                  ('t_min', 'DATETIME'), ('t_max', 'DATETIME'), ('items', 'INT')]
    table_name = 'colls_log'
