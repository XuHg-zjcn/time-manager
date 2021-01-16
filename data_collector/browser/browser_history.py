"""
Created on Tue Nov 17 14:37:07 2020

@author: xrj
"""

import sqlite3

from data_collector.auto_collect import Collector
from sqlite_api.task_db import Plan


class BrowserHistory(Collector):
    sql = None
    dbtype = 1001
    table_name = 'browser'
    coll_name = 'browser history'
    plan_name = 'browser visit'

    def __init__(self, source_path, plan_name=plan_name):
        self.source_path = source_path
        super().__init__(plan_name)

    def run(self, clog, tdb):
        conn = sqlite3.connect(self.source_path)
        cur = conn.cursor()
        res = cur.execute(self.sql)

        items = 0
        try:
            prev = next(res)[0]
        except StopIteration:
            clog.add_log(self.cid, None, None, 0)
            return
        t_min = prev
        last_start = prev
        for curr, in res:  # TODO: probably curr > current timestamp
            if curr - prev > 15*60:  # use t_max only for auto update
                if prev - last_start > 15*60 and last_start >= self.t_max:
                    try:
                        plan = Plan(rec_id=self.cid, name=self.plan_name,
                                    sta=last_start, end=prev)
                        tdb.add_aitem(plan)
                    except ValueError as e:
                        print(e)
                    else:
                        items += 1
                last_start = curr
            prev = curr
        t_max = prev
        clog.add_log(self.cid, t_min, t_max, items)
