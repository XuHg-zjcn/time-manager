#!/bin/python
import utmp
from sqlite_api.collect_data import cdt
from commd_line.init_config import conn
from .auto_collect import Collector


class wtmp_db(Collector):
    def __init__(self):
        self.path = '/var/log/wtmp'
        self.name = 'wtmp_db'

    def run(self):
        with open(self.path, 'rb') as fd:
            items = 0
            t_sta = None
            t_end = None
            buf = fd.read()
            for entry in utmp.read(buf):
                if entry.user == 'runlevel':
                    t_sta = entry.sec + entry.usec/1e6
                elif entry.user == 'shutdown' and t_sta is not None:
                    t_end = entry.sec + entry.usec/1e6
                    if t_end > t_sta:
                        cdt.insert({'rec_id':self.db_fields['id'],
                                    'type_id':0,
                                    'sta':t_sta,
                                    'end':t_end,
                                    'num':0})
                        items += 1
        cdt.commit()
        print(cdt.conn)
        return None, t_end, items
