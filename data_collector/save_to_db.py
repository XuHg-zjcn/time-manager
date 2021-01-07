#!/bin/python
import sqlite3
from .wtmp import wtmp_iter
from sqlite_api.task_db import TaskTable, Plan, PlanTime
from commd_line.init_config import init_config

conf = init_config()
db_path = conf['init']['db_path']
conn = sqlite3.connect(db_path)

tdb = TaskTable(conn, commit_each=False)
for i in wtmp_iter():
    print(i)
    try:
        plan = Plan(PlanTime(i[0], i[1]), i[2]+2, 'computer_running')
        tdb.add_aitem(plan)
    except ValueError as e:
        print(e)
tdb.commit()
conn.close()
print(tdb.conn)
