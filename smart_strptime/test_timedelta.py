#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 20:21:39 2020

@author: xrj
"""
# import cProfile
from basetest import BaseTest
import sys
sys.path.append("..")
from smart_strptime import TimeDelta_str

test_ok = ['1d 12:10', '12:34:12', '12m34s', '1h12m34s']
test_err = ['1s 12:14', ' ', '']

if __name__ == '__main__':
    bt = BaseTest(TimeDelta_str, test_ok, test_err)
    bt.test_debug()
    bt.test_speed_Nrepeat()
    # cProfile.run('bt.test_speed_Nrepeat()', sort=2)
