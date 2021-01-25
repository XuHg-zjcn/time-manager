#!/bin/python
from .wtmp import wtmp_iter
from sqlite_api.task_db import TaskTable, Plan, PlanTime
from commd_line.init_config import conn

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
