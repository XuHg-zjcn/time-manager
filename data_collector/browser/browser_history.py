#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:37:07 2020

@author: xrj
"""

import sqlite3
import sys
sys.path.append('../')
sys.path.append('../../')
from sqlite_api.TODO_db import TODO_db, Plan, PlanTime


def browser_history(browser_db_path, my_db_path, sql,
                    table_name='browser', plan_name='visit',
                    plan_dbtype=1):
    """Use browser history export to my db.

    browser_db_path:
        Firefox 'places.sqlite'
        Chrome 'History'
    my_db_path: output db path
    sql: execute sql to get visits unix stamp:
        Firefox: 'SELECT visit_date/1000000 FROM moz_historyvisits'
        Chorme: 'SELECT visit_time/1000000-11644473600 FROM visits'
    plan_name: name to creat plan
    plan_dbtype: type to creat plan
    """
    conn = sqlite3.connect(browser_db_path)  # browser db
    c = conn.cursor()
    res = c.execute(sql)

    tdb = TODO_db(db_path=my_db_path,
                  table_name=table_name, commit_each=False)  # my db
    n = 0
    prev = next(res)[0]
    last_start = prev
    for curr, in res:
        if curr - prev > 15*60:
            if prev - last_start > 15*60:
                try:
                    plan = Plan(PlanTime(last_start, prev),
                                plan_dbtype, plan_name)
                    tdb.add_aitem(plan)
                except ValueError as e:
                    print(e)
                else:
                    n += 1
            last_start = curr
        prev = curr
    print('browser history {} found'.format(n))
    tdb.commit()
    tdb.close()
