#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 13:30:37 2020

@author: xrj
"""
from enum import Enum                      # L0 built-in model
from my_str import Part, BigPart, My_str   # L2 my_str
from my_str import sType, sType2re_c2
from basetime import UType, UxType         # L3 basetime define
# level of the module is L4


weekday_full = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
weekday_short = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']

month_full = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'Spetember', 'October', 'November', 'December']
month_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Spet', 'Oct', 'Nov', 'Dec']

eType = Enum('eType', 'weekday month ampm')  # english str part type
fType = Enum('fType', 'full short')          # english str part full or short
# eType and fType to str list, unused
eng_strs = {(eType.weekday, fType.full ): weekday_full,
            (eType.weekday, fType.short): weekday_short,
            (eType.month,   fType.full ): month_full,
            (eType.month,   fType.short): month_short}


class Date_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)
        self.date_p = BigPart(self, 'date', UxType['Date'])

    def process(self):
        self.english_month_weekday()
        self.get_allsType_parts(sType2re_c2)
        self.find_date(8)         # find YYYYMMDD
        if ('time_found' in self.flags) or ('fd642' in self.flags):
            self.find_date(4)     # find YYYY, MMDD
            self.find_date(6)     # find YYYYMM, YYMMDD
            self.unused_chooise()
            self.onlyone_unused_num_as_day()

    def english_month_weekday(self):
        """find english str"""
        month = self.find_strs(month_short, puls1=True)
        weekday = self.find_strs(weekday_short, puls1=False)
        if month is not None:
            self.date_p[UType.month] = month
        if weekday is not None:
            self.date_p[UType.weekday] = weekday

    def find_date(self, digts):
        def num8(self, part, s, e, inti):
            if e-s == 8:
                self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
                self.date_p[UType.month] = Part(self, (s+4, s+6), sType.num)
                self.date_p[UType.day  ] = Part(self, (s+6, e  ), sType.num)
                return True
            return False

        def num6(self, part, s, e, inti):
            def YYYYMM(self, s, e):
                self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
                self.date_p[UType.month] = Part(self, (s+4, e  ), sType.num)

            def YYMMDD(self, s, e):
                self.date_p[UType.year ] = Part(self, (s,   s+2), sType.num)
                self.date_p[UType.month] = Part(self, (s+2, s+4), sType.num)
                self.date_p[UType.day  ] = Part(self, (s+4, e  ), sType.num)

            if e-s == 6:
                if 'YY2' in self.flags:
                    if 191300 <= inti < 210000:  # TODO: add Waring
                        YYYYMM(self, s, e)       # probably not accurate
                    else:
                        YYMMDD(self, s, e)
                else:
                    YYYYMM(self, s, e)
                return True
            return False

        def num4(self, part, s, e, inti):
            if e-s == 4:
                if 1970 <= inti < 2050:
                    self.date_p[UType.year ] = Part(self, (s, e  ), sType.num)
                elif 101 <= inti <= 1231:
                    self.date_p[UType.month] = Part(self, (s, s+2), sType.num)
                    self.date_p[UType.day  ] = Part(self, (s+2, e), sType.num)
                return True
            return False

        nums = self.unused_parts.subset['num']
        for part in nums:
            s = part.span[0]
            e = part.span[1]
            match = part.part_vstr()
            inti = int(match)

            func = {8: num8, 6: num6, 4: num4}[digts]
            if func(self, part, s, e, inti) is True:
                nums.remove(part)
