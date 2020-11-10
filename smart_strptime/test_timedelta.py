#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 20:21:39 2020

@author: xrj
"""
import sys
sys.path.append("..")
from smart_strptime import TimeDelta_str


def test():
    test_ok = ['1d 12:10', '12:34:12', '12m34s', '1h12m34s']
    test_err = ['1s 12:14']
    dt_str = TimeDelta_str('1h12m34s')
    dt_str.process()
    print(dt_str)
    print('t_uints:', repr(dt_str.t_units))
    print('time_p: ', repr(dt_str.time_p))
    print('-------------------------------------------------')
    td = dt_str.as_timedelta()
    print('time delta :', td)
    print('total {}sec'.format(dt_str.as_sec()))
    return dt_str

if __name__ == '__main__':
    dt_str = test()
