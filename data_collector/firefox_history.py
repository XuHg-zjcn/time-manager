#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 02:17:41 2020

@author: xrj
"""

import sqlite3

import sys
sys.path.append('../')
from sqlite_api.TODO_db import TODO_db, Plan, PlanTime
tdb = TODO_db(db_path='firefox_history.db', commit_each=False)

db_path = 'places.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()
sql = 'SELECT visit_date FROM moz_historyvisits'
res = c.execute(sql)

n = 0
prev = next(res)[0]
last_start = prev
for curr, in res:
    if curr - prev > 15*60*1e6:
        if prev - last_start > 15*60*1e6:
            try:
                plan = Plan(PlanTime(last_start/1e6, prev/1e6), 1, 'firefox')
                tdb.add_aitem(plan)
            except ValueError as e:
                print(e)
            else:
                n += 1
        last_start = curr
    prev = curr
print(n)
tdb.commit()
tdb.close()
print(tdb.conn)
