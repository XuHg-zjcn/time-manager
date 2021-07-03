"""
Created on Tue Nov 17 14:37:07 2020

@author: xrj
"""

import sqlite3

from data_collector.auto_collect import Collector
from sqlite_api.collect_data import cdt


class BrowserHistory(Collector):
    sql = None

    def __init__(self, name, source_path):
        self.source_path = source_path
        super().__init__(name)

    def run(self, clog):
        conn = sqlite3.connect(self.source_path)
        cur = conn.cursor()
        res = cur.execute(self.sql)

        items = 0
        try:
            prev = next(res)[0]
        except StopIteration:
            clog.add_log(self.db_fields['id'], None, None, 0)
            return
        t_min = prev
        last_start = prev
        for curr, in res:  # TODO: probably curr > current timestamp
            if curr - prev > 15*60:  # use t_max only for auto update
                if prev - last_start > 15*60 and\
                      last_start >= self.db_fields['t_max']:
                    try:
                        cdt.insert({'rec_id':self.db_fields['id'],
                                    'sta':last_start, 'end':prev})
                    except ValueError as e:
                        print(e)
                    else:
                        items += 1
                last_start = curr
            prev = curr
        t_max = prev
        clog.add_log(self.db_fields['id'], t_min, t_max, items)
