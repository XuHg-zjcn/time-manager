"""
Created on Sat Nov  7 16:04:48 2020

@author: xrj
test time_str model speed and errors
"""

import os
import time
import traceback


class BaseTest:
    def __init__(self, test_class, test_ok, test_err):
        self.test_class = test_class
        self.test_ok = test_ok
        self.test_err = test_err
        self.n_test = len(test_ok) + len(test_err)

    def __test_a_list_str(self, test_list, expect_err=False,
                          print_traceback=True):
        t_sum = 0
        for i in test_list:
            tstr = self.test_class(i)
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

    def __test_quiet(self, test_list):
        t_sum = 0
        for i in test_list:
            try:
                t0 = time.process_time()
                tstr = self.test_class(i)
                tstr.process_check()
            except Exception:
                pass
            finally:
                t1 = time.process_time()
                t_sum += t1 - t0
        return t_sum

    def test_speed_Nrepeat(self, N_rep=100):
        print('')
        print('speed test:')
        t_sum = 0
        for i in range(N_rep):
            t_sum += self.__test_quiet(self.test_ok)
            t_sum += self.__test_quiet(self.test_err)
        t_sum *= 1000  # sec to ms
        print('{:.2f}ms/({}*{})test, {:.3f}ms per test'
              .format(t_sum, self.n_test, N_rep, t_sum/(self.n_test*N_rep)))

    def test_debug(self):
        os.system('clear')
        t_sum = 0
        print('################Test_OK, should no error!!!!!!!!!!!!!!!!!!!!')
        t_sum += self.__test_a_list_str(self.test_ok,
                                        expect_err=False, print_traceback=True)
        print('##########Test_Err, should happend error each item!!!!!!!!!!')
        t_sum += self.__test_a_list_str(self.test_err,
                                        expect_err=True, print_traceback=False)
        t_sum *= 1000
        print('{}tests, total {:.2f}ms, {:.3f}ms per test'
              .format(self.n_test, t_sum, t_sum/self.n_test))
        print('------------------------------------------------------------')

    def test(self):
        self.test_debug()
        self.test_speed_Nrepeat()
