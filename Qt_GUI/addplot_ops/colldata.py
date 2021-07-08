import sqlite3
from my_libs.sqltable import SqlTable
from intervaltree.intervaltree import IntervalTree
from sqlite_api.collect_data import cdt

def PlotCollData(win, name, color, conds={}):
    cdt.get_conds_execute(conds, ['sta', 'end'])
    df = cdt.get_conds_execute(conds, ['sta', 'end'])
    ivt = IntervalTree.from_tuples(df)
    win.dt2d_plot.draw_ivtree(ivt, default_color=color, name=name)

def PlotDBInterval(win, name, color,
                   db_path, table_name, sta_name, end_name,
                   k=1, b=0, conds={}):
    where_str = SqlTable._conds2where(conds)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    df = cur.execute(f"SELECT k*{sta_name}+b, k*{end_name}+b FROM {table_name} WHERE {where_str}")
    ivt = IntervalTree.from_tuples(df)
    win.dt2d_plot.draw_ivtree(ivt, default_color=color, name=name)

def PlotDBPoints(win, name, color,
                 db_path, table_name, col_name,
                 k=1, b=0, conds={}):
    where_str, params = SqlTable._conds2where(conds)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    sql = f"SELECT {k}*{col_name}+{b} FROM {table_name} {where_str}"
    exec = cur.execute(sql, params)
    lst = map(lambda x:x[0], exec)
    win.dt2d_plot.draw_points(lst, color=color)
