#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 12:26:48 2020

@author: xrj
"""
import time
from datetime import date
import numpy as np
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageDraw , ImageFont

weekdays_en = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekdays_zh = ['一', '二', '三', '四', '五', '六', '日']
weekdays_num = [str(i) for i in range(1, 8)]
months_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Spet', 'Oct', 'Nov', 'Dec']
months_num = [str(i) for i in range(1, 13)]

"""
day blocks in week-day 2d plot:
####################
##--2h-->##       ##
## 12*12 ## 12*12 ##
##       ##       ##
####################
##       ##       ##
## 12*12 ## 12*12 ##
##       ##       ##
####################
14*14 per block, 2px border, 12*12 vaild.
2hours per row, 10minute per pixel.


Generate output:
    |<-----------w*365=730------------->|
  p1.__________week-day 2d____|w*7|_____|____
Mon |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_| ... |  ^
Tue |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_| ... |  |
Wed |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_| ... |  h1*7=98
... | ....,,..................... | ... |  |
Sun |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_____|__v_
    :                                   :  ^ h2=16
  p2.__________day-time 2d______|w|_____:__v_
  0 ||||||||||||||||||||||||||||||| ... |  ^
  1 ||||||||||||||||||||||||||||||| ... |  |
  2 ||||||||||||||||||||||||||||||| ... |  h3=288
... ||||||||||||||||||||||||||||||| ... |  |
 23 ||||||||||||||||||||||||||||||| ... |__v_
    1..31, 1..28, 1..31            1..31
     Jan    Feb    Mar     ...      Dec
"""
class gene_bkgd:
    def __init__(self, year, w=2, h2=7, h3=288):
        self.year = year
        self.p1 = (19, 6)
        w = 2     # 2px width per day
        self.h1 = 14   # day block is square
        self.h2 = h2#= 20    # space between week-day 2d and day-time 2d
        self.h3 = h3#= 288   # 5minute per pixel height
        self.p2 = (self.p1[0], self.p1[1]+self.h1*7+h2)
        self.img = Image.new('RGB', (760, 420))
        self.draw = ImageDraw.Draw(self.img)
        self.doy_months()

    def doy_months(self):
        self.doys = []
        d11 = date(self.year, 1, 1)
        for y, m in [(self.year, i) for i in range(1, 13)]+[(self.year+1, 1)]:
            dx1 = date(y, m, 1)
            doy = (dx1-d11).days # day_of_year
            self.doys.append(doy)

    def weekday_label(self):
        for i, wd in enumerate(weekdays_en):
            self.draw.text((0, i*self.h1+self.h1//2), wd)

    def hours_label(self, n):
        if 24 % n != 0:
            raise ValueError("n can't div by 24")
        x0, y0 = self.p2
        y1 = y0 + np.linspace(0, self.h3, n+1, dtype=np.int64)
        hours = np.linspace(0, 24, n+1, dtype=np.int64)
        for y, h in zip(y1, hours):
            self.draw.text((0, y-5), "{:>2}".format(h))

    def months_label(self):
        x1, y1 = self.p2
        x1 -= 2
        y1 += self.h3+5
        for i, doy in enumerate(self.doys):
            m = str(i+1 if i<12 else 1)
            xb = -3 if len(m)==2 else 0
            self.draw.text((x1+doy*2+xb, y1), m)

    def img2arr(self):
        self.arr = np.array(self.img)

    def draw_week_day_grids(self, color=(255, 255, 255)):
        xm, ym = self.p1
        xM = xm + 366*2
        yM = ym + self.h1*7 + 2
        d11 = date(self.year, 1, 1)
        xb = (6 - (d11.weekday()-1)%7)*2  # Mon0, Tue12, Wed10, Thur8, ... Sun2
        self.arr[ym  :yM:14,   xm:xM] = color     # upper
        self.arr[ym+1:yM:14,   xm:xM] = color     # lower
        self.arr[ym:yM,   xm+xb  :xM:14] = color  # left
        self.arr[ym:yM,   xm+xb+1:xM:14] = color  # right

    def draw_hours_scale(self, n, dx, color=(255, 255, 255)):
        x0, y0 = self.p2
        y1 = y0 + np.linspace(0, self.h3, n+1,
                              dtype=np.int64)  # 25 points, 0...24
        self.arr[y1, x0-dx:x0] = color

    def draw_months(self, dy, color=(255, 255, 255)):
        y0 = self.p2[1]
        x1, y1 = self.p2
        y1 += self.h3
        for doy in self.doys:
            self.arr[y0-dy:y0, x1+doy*2] = color
            self.arr[y1:y1+dy, x1+doy*2] = color

    def draw_dt2d_border(self, color=(255, 255, 255)):
        x0, y0 = self.p2
        x1 = x0 + 366*2
        y1 = y0 + self.h3
        self.arr[y0, x0:x1] = color    # upper
        self.arr[y1, x0:x1] = color    # lower
        self.arr[y0:y1, x0] = color    # left
        self.arr[y0:y1, x1] = color    # right

    def show(self):
        img = Image.fromarray(self.arr).convert('RGB')
        img.show()

bkgd = gene_bkgd(2020)
bkgd.weekday_label()
bkgd.hours_label(6)
bkgd.months_label()
bkgd.img2arr()
bkgd.draw_week_day_grids()
bkgd.draw_hours_scale(6, 5)
bkgd.draw_hours_scale(24, 2)
bkgd.draw_months(5)
bkgd.draw_dt2d_border()
bkgd.show()
