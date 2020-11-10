#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 16:04:48 2020

@author: xrj
test time_str model speed and errors
"""

import os
import time
import traceback
import cProfile

import sys
sys.path.append("..")
from smart_strptime import TimeDelta_str as test_class

test_ok = ['Wed 28/Oct 12:34:56.123',
           '20201030', '1030', '30 10:30', '10:22 PM',
           '2020 10 5', '2020/11/5', '2020-11/5', '2020 Nov 5',
           '2020 5 Nov', '5 Nov 2020', '5/Nov/2020', '5 Nov. 2020',
           '202010', '2020 10', '2020 Nov', '2020Nov', '2020 Nov.',
           '2020 November 7', '7 November.2020', '7/Nov. 2020', '7Nov2020',
           '7/Nov/2020 18:56', '2020.11.7',
           '201107', '197001', '191015', '220202']
test_err = ['12:34:56:12', '12.34:34', 'Oct:12', '2020:12', '12 20:12 Oct',
            '10:30 a', 'abcd', '12:ab', '', ' ']
n_test = len(test_ok) + len(test_err)


def test_a_list_str(test_list, expect_err=False, print_traceback=True):
    t_sum = 0
    for i in test_list:
        tstr = test_class(i)
        t0 = time.time()
        try:
            tstr.process_check()
        except Exception as e:
            err = e
        else:
            err = None
        finally:
            t1 = time.time()
            t_sum += t1 - t0
            print(tstr)
            err_happend = err is not None
            if err_happend and print_traceback:
                traceback.print_exc()
            elif err_happend and not print_traceback:
                print('Error: ', err)
            else:
                print('no error')
            if err_happend != expect_err:
                print('error not expect, expect is {}, but result is {}'
                      .format(expect_err, err_happend))
            print('process {:.3f}ms'.format((t1-t0)*1000))
        print()
    return t_sum


def test_quiet(test_list):
    t_sum = 0
    for i in test_list:
        try:
            t0 = time.process_time()
            tstr = test_class(i)
            tstr.process_check()
        except Exception:
            pass
        finally:
            t1 = time.process_time()
            t_sum += t1 - t0
    return t_sum


def test_speed_Nrepeat(N_rep=200):
    print('')
    print('speed test:')
    t_sum = 0
    for i in range(N_rep):
        t_sum += test_quiet(test_ok)
        t_sum += test_quiet(test_err)
    t_sum *= 1000  # sec to ms
    print('{:.2f}ms/({}*{})test, {:.3f}ms per test'
          .format(t_sum, n_test, N_rep, t_sum/(n_test*N_rep)))


def test_check():
    os.system('clear')
    t_sum = 0
    print('################Test_OK, should no error!!!!!!!!!!!!!!!!!!!!')
    t_sum += test_a_list_str(test_ok, expect_err=False, print_traceback=True)
    print('##########Test_Err, should happend error each item!!!!!!!!!!')
    t_sum += test_a_list_str(test_err, expect_err=True, print_traceback=False)
    t_sum *= 1000
    print('{}tests, total {:.2f}ms, {:.3f}ms per test'
          .format(n_test, t_sum, t_sum/n_test))
    print('------------------------------------------------------------')


# test codes
if __name__ == '__main__':
    n_test = len(test_ok)+len(test_err)
    test_check()
    cProfile.run('test_speed_Nrepeat()', sort=2)
    test_speed_Nrepeat()
