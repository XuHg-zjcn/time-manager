#!/bin/python
from wtmp import wtmp_iter
import sys
sys.path.append('../')
from sqlite_api.TODO_db import TODO_db, Plan, PlanTime
tdb = TODO_db(db_path='linux.db', table_name='wtmp', commit_each=False)
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
