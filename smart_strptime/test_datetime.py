#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 02:51:06 2020

@author: xrj
"""

import cProfile
from basetest import BaseTest
import sys
sys.path.append("..")
from smart_strptime import DateTime_str

test_ok = ['Wed 28/Oct 12:34:56.123',
           '20201030', '1030', '30 10:30', '10:22 PM',
           '2020 10 5', '2020/11/5', '2020-11/5', '2020 Nov 5',
           '2020 5 Nov', '5 Nov 2020', '5/Nov/2020', '5 Nov. 2020',
           '202010', '2020 10', '2020 Nov', '2020Nov', '2020 Nov.',
           '2020 November 7', '7 November.2020', '7/Nov. 2020', '7Nov2020',
           '7/Nov/2020 18:56', '2020.11.7',
           '201107', '197001', '191015', '220202',
           '11.11 0:00', '2020.11.11 00:00', '20.11.11 0:00:00']
#test_ok = ['11.11 0:00']
test_err = ['12:34:56:12', '12.34:34', 'Oct:12', '2020:12', '12 20:13 Oct',
            '10:30 a', 'abcd', '12:ab', '', ' ']
#test_err = ['12 20:13 Oct']

if __name__ == '__main__':
    bt = BaseTest(DateTime_str, test_ok, test_err)
    bt.test_debug()
    bt.test_speed_Nrepeat()
    #cProfile.run('bt.test_speed_Nrepeat()', sort=2)
