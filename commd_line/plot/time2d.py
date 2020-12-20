#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 18:37:44 2020

@author: xrj
"""
import os
from datetime import datetime
import time
from my_libs.ivtree2 import Iv2
from ..plot.left_right import sync_ivtree

timezone = time.timezone


def gen_head(char_per_h, month):
    head = '\033[1;32m{:>2}\033[00m'  # Bold green month number
    for i in range(24):
        head += '|{:<{}}'.format(i, char_per_h-1)   # normal font for hours
    return head.format(month)


def Time2D(ivtree, char_per_h=4):
    """
    Plot time2d view.

    x-axis(columns) time, y-axis(rows) date.
    IntervalTree's data is color of plot Interval
    """
    assert char_per_h >= 3
    date_min = int(ivtree.begin() - timezone)//86400
    date_max = int(ivtree.end() - timezone)//86400
    wide = 24*char_per_h*8
    n = 0
    for i in range(date_min, date_max+1):
        day_sta = i*86400 + timezone
        day_end = (i+1)*86400 + timezone
        dati = datetime.fromtimestamp(day_sta)
        if n == 0 or dati.day == 1:
            print(gen_head(char_per_h, dati.month))
        sp_in_day = ivtree & Iv2(day_sta, day_end)
        sp_in_day = sp_in_day.apply_each_interval(
                    lambda x: int((x-day_sta)*(wide/86400)))
        # TODO use mean color
        sp_in_day.merge_overlaps(data_reducer=lambda a, b: a)
        bar = sync_ivtree(sp_in_day, end=wide)
        print('{:>2}{}'.format(dati.day, bar))
        n += 1


def Time2D_AutoSize(ivtree):
    try:
        cols = os.get_terminal_size().columns
    except OSError:
        char_per_h = 4
    else:
        char_per_h = (cols-2)//24
    Time2D(ivtree, char_per_h)
