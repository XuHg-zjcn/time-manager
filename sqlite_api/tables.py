import time
from pickle import dumps

from Qt_GUI.cluster import TxtClr
from sqlite_api.argb import ARGB
from sqlite_api.task_db import SqlTable
from my_libs.dump_table import DumpTable


class CollTable(DumpTable):
    name2dtype = [('name', 'TEXT'),   # name of collector
                  ('start_mode', 'INT'),  # -1 custom source path, 0 manual, 1 batch, 2 auto
                  ('dump', 'BLOB'),   # pickle.dumps bytes
                  ('runs', 'INT'),    # runs counts
                  ('items', 'INT'),   # items counts
                  ('t_max', 'REAL'),  # max timestamp of record
                  ('t_last', 'REAL'), # timestamp of last run
                  ('color', 'INT')]   # color for plot
    table_name = 'collectors'

    def add_item(self, obj, start_mode=1, color=0xffffff00, commit=True):
        if isinstance(color, int):
            pass
        elif isinstance(color, ARGB):
            color = color.ARGBi()
        else:
            raise TypeError('unsupported color type:', type(color))
        self.insert([obj.name, start_mode, dumps(obj),
                     0, 0, 0, time.time(), color], commit)

    def find_txtclr(self, cid):
        txt, clr = self.get_conds_onlyone({'id': cid}, ['name', 'color'],
                                          ['{}'.format(cid), 0xff00ffff])
        clr = ARGB.from_argb(clr).inv_bin()
        return TxtClr(txt, clr)


class CollLogTable(SqlTable):
    name2dtype = [('cid', 'INT'),     # id of collector
                  ('run_i', 'INT'),   # n-th run of the collector
                  ('t_run', 'REAL'),  # time when insert to the table
                  ('t_min', 'REAL'),  # min start time of items
                  ('t_max', 'REAL'),  # max stop time of items
                  ('items', 'INT')]   # count items of this run
    table_name = 'colls_log'
