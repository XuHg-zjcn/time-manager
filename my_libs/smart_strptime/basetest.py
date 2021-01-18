"""
Created on Sat Nov  7 16:04:48 2020

@author: xrj
test time_str model speed and errors
"""

import time
import traceback

red = '\033[1;31m'
green = '\033[1;32m'
d_t = '\033[1;36m'
end = '\033[00m'


class BaseTest:
    def __init__(self, test_class, test_ok, test_err):
        self.test_class = test_class
        self.test_ok = test_ok
        self.test_err = test_err

    def __test_a_list_str(self, test_list, should_err=False,
                          print_traceback=True):
        t_sum = 0
        n_err = 0
        for i in test_list:
            tstr = self.test_class(i)
            t0 = time.time()
            try:
                tstr.process_check()
            except Exception as e:
                if print_traceback:
                    traceback.print_exc()
                err = e
                n_err += 1
            else:
                err = None
            finally:
                t1 = time.time()
                t_sum += t1 - t0
                print(tstr)
                err_happend = err is not None
                if err_happend:
                    print('{}Error: {}{}'.format(red, end, err))
                else:
                    print('{}no error{}'.format(green, end))
                color_happ = red if err_happend else green
                if err_happend != should_err:
                    print('error not correct, expect is {}, result is {}{}!!{}'
                          .format(should_err, color_happ, err_happend, end))
                print('process {:.3f}ms'.format((t1-t0)*1000))
            print()
        t_sum *= 1000
        n = len(test_list)
        n_ok = n - n_err
        print('{}tests, total {:.2f}ms, {}{:.3f}ms per test{}'
              .format(n, t_sum, d_t, t_sum/n, end))
        color_err = red if n_err != 0 else ''
        color_ok = green if n_ok != 0 else ''
        should = 'error' if should_err else 'OK'
        color_should = red if should_err else green
        print('{}err:{}{}{}, {}OK:{}{}{}, {}shoud all {}{}'
              .format(color_err, red, n_err, end,
                      color_ok, green, n_ok, end,
                      color_should, should, end))

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
        n = len(self.test_ok) + len(self.test_err)
        per = t_sum/(n*N_rep)
        print('{:.2f}ms/({}*{})test, {}{:.3f}ms per test{}'
              .format(t_sum, n, N_rep, d_t, per, end))

    def test_debug(self):
        print('{}################Test_OK, should no error!!!!!!!!!!!!!!!!!!!{}'
              .format(green, end))
        self.__test_a_list_str(self.test_ok,
                               should_err=False, print_traceback=True)
        print('------------------------------------------------------------')
        print('{}#########Test_Err, should happend error each item!!!!!!!!!{}'
              .format(red, end))
        self.__test_a_list_str(self.test_err,
                               should_err=True, print_traceback=False)
        print('------------------------------------------------------------')

    def test(self):
        self.test_debug()
        self.test_speed_Nrepeat()
