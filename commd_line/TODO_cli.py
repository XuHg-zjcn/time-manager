#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from plot.time2d import Time2D
import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from Qt_GUI.pyqtgraph_plot import dt2p, hold
from commd_line.init_config import init_config
from smart_strptime.time_input import CLI_Inputer, OutType

conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)
cti = CLI_Inputer(output_type=OutType.timestamp)


def fixed():
    name = input('名称:')
    sta_time = cti('开始时间:')
    end_time = cti('结束时间:')
    use_time = end_time - sta_time
    pt = PlanTime(sta_time, end_time, use_time)
    p = Plan(pt, 1, name)
    tdb.add_aitem(p)


op = input('''请输入要进行的操作:
1. 添加任务
2. 列出任务
3. 删除任务
4. 修改任务
''')
if op == '1':
    fixed()
elif op == '2':
    sta = cti('开始时间:')
    end = cti('结束时间:')
    plans = tdb.get_aitem({'sta_time': (sta, end), 'end_time': (sta, end)})
    print(plans)
    ivtree = plans.get_ivtree()
    if conf['show']['type'] == 'unicode':
        Time2D(ivtree)
    if conf['show']['type'] == 'pyqtgraph':
        dt2p.update_ivtree(ivtree)
        hold()
else:
    print('输入有误，请输入正确的序号1-4')
