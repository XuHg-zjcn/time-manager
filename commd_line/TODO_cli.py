#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time_input import Time_input
from plot.time2d import Time2D
import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from my_libs.ivtree2 import IvTree2

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
        ivtree[sta:end] = clr_tab[plan.dbtype]  # show color
    Time2D(ivtree)
else:
    print('输入有误，请输入正确的序号1-4')
