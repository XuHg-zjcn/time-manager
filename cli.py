#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from commd_line.plot.time2d import Time2D
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from sqlite_api.colors import ARGB
from commd_line.init_config import init_config
from smart_strptime.time_input import CLI_Inputer, OutType
from data_collector import auto_collect

conf = init_config()
db_path = conf['init']['db_path']
table_name = conf['init']['table_name']
tdb = TODO_db(db_path=db_path, table_name=table_name)
cti = CLI_Inputer(output_type=OutType.timestamp)


def add_task():
    name = input('名称:')
    dbtype = int(input('类型编号:'))
    sta_time = cti('开始时间:')
    end_time = cti('结束时间:')
    num = int(input('整数参数:'))
    color = ARGB.fromStr(input('颜色:'))
    use_time = end_time - sta_time
    pt = PlanTime(sta_time, end_time, use_time)
    p = Plan(pt, dbtype, name, num, color=color)
    tdb.add_aitem(p)


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
    plans = tdb.get_aitem({'sta_time': (sta, end), 'end_time': (sta, end)})
    print(plans)
    ivtree = plans.get_ivtree()
    Time2D(ivtree)
elif op == '3':
    auto_collect.cli()
else:
    print('输入有误，请输入正确的序号1-4')
