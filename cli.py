#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from commd_line.init_config import conn
from commd_line.plot.time2d import time2d_autosize
from sqlite_api.tables import colls
from sqlite_api.task_db import Plan, tdb
from my_libs.smart_strptime import CLI_Inputer, OutType
from data_collector import auto_collect

cti = CLI_Inputer(output_type=OutType.timestamp)

ac = auto_collect.Collectors(conn)


def input_op():
    return input('''请输入要进行的操作:
1. 添加任务
2. 列出任务
3. 收集数据
4. 修改任务
''')


def add_task():
    name = input('名称:')
    sta_time = cti('开始时间:')
    end_time = cti('结束时间:')
    num = int(input('整数参数:'))
    state = int(input('状态:'))
    p = Plan(name=name, num=num, sta=sta_time, end=end_time, state=state)
    tdb.insert(p)
    tdb.conn.commit()


def list_tasks():
    sta = cti('开始时间:')
    end = cti('结束时间:')
    plans = tdb.get_conds_plans({'sta': (sta, end), 'end': (sta, end)})
    print(plans)
    ivtree = plans.get_ivtree(lambda p: Plan(p).get_collect_color(colls))
    time2d_autosize(ivtree)


if __name__ == '__main__':
    tdb.print_doings()
    tdb.print_need()
    op = input_op()
    if op == '1':
        add_task()
    elif op == '2':
        list_tasks()
    elif op == '3':
        ac.cli()
    else:
        print('输入有误，请输入正确的序号1-4')
