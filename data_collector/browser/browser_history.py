"""
Created on Tue Nov 17 14:37:07 2020

@author: xrj
"""

import sqlite3
import sys

from ..auto_collect import Collector

sys.path.append('../')
sys.path.append('../../')
from sqlite_api.task_db import Plan, PlanTime


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
        for curr, in res:
            if curr - prev > 15*60:
                if prev - last_start > 15*60:
                    try:
                        plan = Plan(PlanTime(last_start, prev),
                                    self.dbtype, self.plan_name)
                        tdb.add_aitem(plan)
                    except ValueError as e:
                        print(e)
                    else:
                        items += 1
                last_start = curr
            prev = curr
        t_max = prev
        clog.add_log(self.cid, t_min, t_max, items)
