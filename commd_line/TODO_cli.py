#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from time_input import Time_input
from intervaltree import IntervalTree
import time

from plot.left_right import sync_ivtree

import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from my_libs.ivtree2 import IvTree2, Iv2

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
    res = tdb.get_aitem({'sta_time': (sta, end), 'end_time': (sta, end)})
    ivtree = IvTree2()
    clr_tab = ['k', 'r', 'y', 'g', 'c', 'b', 'm']
    print(Plan.str_head)
    for plan in res:
        print(plan)
        sta = plan.p_time.sta_time
        end = plan.p_time.end_time
        ivtree[sta:end] = clr_tab[plan.dbtype]
    date_min = int(ivtree.begin()+8*3600)//86400
    date_max = int(ivtree.end()+8*3600)//86400
    head = '\033[1;32m{:>2}\033[00m'  # Bold green month number
    for i in range(24):
        head += '|{:<2} '.format(i)   # normal font for hours
    head = head[:-1]    # example: 11|0  |1  |2  |3  |4...
    n = 0
    for i in range(date_min, date_max+1):
        day_sta = i*86400-8*3600
        day_end = (i+1)*86400-8*3600
        dati = datetime.fromtimestamp(day_sta)
        if n == 0 or dati.day == 1:
            print(head.format(dati.month))
        sp_in_day = ivtree & Iv2(day_sta, day_end)
        sp_in_day = sp_in_day.apply_each_interval(lambda x: int((x-day_sta)*(768/86400)))
        bar = sync_ivtree(sp_in_day, end=768)
        print('{:>2}{}'.format(dati.day, bar))
        n += 1
else:
    print('输入有误，请输入正确的序号1-4')
