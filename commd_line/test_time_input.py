#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 05:03:38 2020

@author: xrj
"""
from time_input import Time_input

test_ok = ['n', 'now', 'n+1.1h', '+1m', '-1.0s', '+1d', 'n+.5h', 'n+0.1s']
test_err = ['+x', 'n+n', 'nx', 'abc', 'n+1hh', 'n+1hm', 'n+hh', ' ', '']

ti = Time_input()


def test(lst):
    for i in lst:
        v = ti.input_str(i)
        print(v)


print('################Test_OK, should no error!!!!!!!!!!!!!!!!!!!!')
test(test_ok)
print('##########Test_Err, should happend error each item!!!!!!!!!!')
test(test_err)
