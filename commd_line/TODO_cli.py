#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from time_input import Time_input
from plot.left_right import Spans_out

import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db, PlanTime, Plan
from smart_strptime.my_lib import span, Spans

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
    sp = Spans()
    clrs = []
    clr_tab = ['k', 'r', 'y', 'g', 'c', 'b', 'm']
    print(Plan.str_head)
    for plan in res:
        print(plan)
        sp.append((plan.p_time.sta_time, plan.p_time.end_time))
        clrs.append(clr_tab[plan.dbtype])
    no_overlappend = sp.merge_insec(merge=False)
    assert no_overlappend
    date_min = int(min(sp)[0]+8*3600)//86400
    date_max = int(max(sp)[1]+8*3600)//86400
    for i in range(date_min, date_max+1):
        day = span(i*86400-8*3600, (i+1)*86400-8*3600)
        dati = datetime.fromtimestamp(day[0])
        sp_in_day = sp & day
        sp_in_day = (sp_in_day - day[0])*(768/86400)
        sp_in_day = sp_in_day.as_int()
        day_str = dati.strftime('%m-%d')
        bar = Spans_out(sp_in_day, ['r']*len(sp_in_day), end=768)
        print(day_str+bar)
else:
    print('输入有误，请输入正确的序号1-4')
