#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 18:37:44 2020

@author: xrj
"""
from datetime import datetime
import time
from my_libs.ivtree2 import Iv2
from plot.left_right import sync_ivtree

timezone = time.timezone
head = '\033[1;32m{:>2}\033[00m'  # Bold green month number
for i in range(24):
    head += '|{:<2} '.format(i)   # normal font for hours
head = head[:-1]    # example: 11|0  |1  |2  |3  |4...

def Time2D(ivtree):
    """
    Plot time2d view.

    x-axis(columns) time, y-axis(rows) date.
    IntervalTree's data is color of plot Interval
    """
    date_min = int(ivtree.begin() - timezone)//86400
    date_max = int(ivtree.end() - timezone)//86400
    n = 0
    for i in range(date_min, date_max+1):
        day_sta = i*86400 + timezone
        day_end = (i+1)*86400 + timezone
        dati = datetime.fromtimestamp(day_sta)
        if n == 0 or dati.day == 1:
            print(head.format(dati.month))
        sp_in_day = ivtree & Iv2(day_sta, day_end)
        sp_in_day = sp_in_day.apply_each_interval(lambda x: int((x-day_sta)*(768/86400)))
        bar = sync_ivtree(sp_in_day, end=768)
        print('{:>2}{}'.format(dati.day, bar))
        n += 1
