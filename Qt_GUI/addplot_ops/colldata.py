import sqlite3
from my_libs.sqltable import SqlTable
from intervaltree.intervaltree import IntervalTree
from sqlite_api.collect_data import cdt
from sqlite_api.timepoint_db import tpd

# 包含数据库操作，请不要移入图形库文件
def PlotCollData(win, name, color, conds={}):
    df = cdt.get_conds_execute(conds, ['sta', 'end'])
    ivt = IntervalTree.from_tuples(df)
    win.dt2d_plot.draw_ivtree(ivt, default_color=color, name=name)

def PlotPoints(win, name, color, conds={}):
    df = tpd.get_conds_execute(conds, ['time', 'desc'])
    tsxx = []
    desc = []
    for t, d in df:
        tsxx.append(t)
        desc.append(d)
    win.draw_points_label(tsxx, desc, color=color, name=name)

def PlotDBInterval(win, name, color,
                   db_path, table_name, sta_name, end_name,
                   k=1, b=0, conds={}):
    where_str = SqlTable._conds2where(conds)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    df = cur.execute(f"SELECT k*{sta_name}+b, k*{end_name}+b FROM {table_name} WHERE {where_str}")
    ivt = IntervalTree.from_tuples(df)
    win.draw_ivtree(ivt, default_color=color, name=name)

def PlotDBPoints(win, name, color,
                 db_path, table_name, col_name,
                 k=1, b=0, conds={}):
    where_str, params = SqlTable._conds2where(conds)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    sql = f"SELECT {k}*{col_name}+{b} FROM {table_name} {where_str}"
    exec = cur.execute(sql, params)
    lst = map(lambda x:x[0], exec)
    win.draw_points(lst, color=color)
