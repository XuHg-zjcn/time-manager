#!/bin/python
from wtmp import wtmp_iter
import sys
sys.path.append('../')
from sqlite_api.task_db import TaskDB, Plan, PlanTime
tdb = TaskDB(db_path='linux.db', table_name='wtmp', commit_each=False)
for i in wtmp_iter():
    print(i)
    try:
        plan = Plan(PlanTime(i[0], i[1]), i[2]+2, 'computer_running')
        tdb.add_aitem(plan)
    except ValueError as e:
        print(e)
tdb.commit()
tdb.close()
print(tdb.conn)
