#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from commd_line.plot.time2d import time2d_autosize
from sqlite_api.tables import CollTable
from sqlite_api.task_db import Plan, TaskTable
from commd_line.init_config import init_config
from smart_strptime.time_input import CLI_Inputer, OutType
from data_collector import auto_collect

conf = init_config()
db_path = conf['init']['db_path']
conn = sqlite3.connect(db_path)
tdb = TaskTable(conn)
colls = CollTable(conn)
cti = CLI_Inputer(output_type=OutType.timestamp)

ac = auto_collect.Collectors(conn, tdb)
ac.run_enable()


def add_task():
    name = input('名称:')
    sta_time = cti('开始时间:')
    end_time = cti('结束时间:')
    num = int(input('整数参数:'))
    state = int(input('状态:'))
    p = Plan(name=name, num=num, sta=sta_time, end=end_time, state=state)
    tdb.insert(p)
    tdb.conn.commit()


tdb.print_doings()
op = input('请输入要进行的操作:\n'
           '1. 添加任务\n'
           '2. 列出任务\n'
           '3. 收集数据\n'
           '4. 修改任务\n')
if op == '1':
    add_task()
elif op == '2':
    sta = cti('开始时间:')
    end = cti('结束时间:')
    plans = tdb.get_conds_plans({'sta': (sta, end), 'end': (sta, end)})
    print(plans)
    ivtree = plans.get_ivtree(lambda p: Plan(p).get_collect_color(colls))
    time2d_autosize(ivtree)
elif op == '3':
    ac.cli()
else:
    print('输入有误，请输入正确的序号1-4')
