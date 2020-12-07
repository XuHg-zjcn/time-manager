#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time_input import Time_input
from plot.time2d import Time2D
import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from Qt_GUI.pyqtgraph_plot import dt2p, hold
from commd_line.init_config import init_config


conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)
ti = Time_input()


def fixed():
    name = input('名称:')
    sta_str = input('开始时间:')
    sta_time = ti.input_str(sta_str)
    end_str = input('结束时间:')
    end_time = ti.input_str(end_str)
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
    sta_str = input('最晚开始:')
    sta = ti.input_str(sta_str)
    end_str = input('最早结束:')
    end = ti.input_str(end_str)
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
