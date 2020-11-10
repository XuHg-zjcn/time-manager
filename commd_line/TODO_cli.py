#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time_input import Time_input

import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan

tdb = TODO_db()
ti = Time_input()


def fixed():
    name = input('名称:')
    sta_str = input('开始时间:')
    sta_time = ti.input_str(sta_str)
    end_str = input('结束时间:')
    end_time = ti.input_str(end_str)
    use_time = end_time - sta_time
    pt = PlanTime(sta_time, end_time, use_time)
    p = Plan(1, name, pt)
    tdb.add_aitem(p)


op = input('''请输入要进行的操作:
1. 添加任务
2. 列出任务
3. 删除任务
4. 修改任务
''')
if op == '1':
    fixed()
