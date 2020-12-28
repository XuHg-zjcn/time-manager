#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 21:43:12 2020

@author: xrj
"""
from datetime import datetime
import time
import re
from smart_strptime.basetime import UType as U


class group:
    def __init__(self, pad, n, ut, skip_on=False):
        """
        :para pad: padding char
        :para n: output length, if n=0, don't use padding
        :para ut: UType
        """
        self.ut = ut
        self.skip_on = skip_on
        if ut == U.subsec:
            self.fmt = '{{:{:s}<.{:d}f}}'.format(pad, n)
        else:
            self.fmt = '{{:{:s}>{:d}d}}'.format(pad, n)
        self.spaces = ' '*n    # skip print

    def format(self, value):
        ret = self.fmt.format(value)
        if self.ut == U.subsec:
            assert 0 <= value < 1
            ret = ret[2:]
        return ret


class MTshort:
    """Get strftime with clear same part.

    compare to last input, find biggest different part, the before part will to
    spaces ' ', after and the part will keep.

    however complete time will keep output.
    if biggest different part is day, month will also keep.
    """

    def __init__(self, fmt='? Y-? m-? d % H:%0M:%0S', init_in=None):
        """Init MTshort object.

        @para fmt: strftime format string, can't change after create
        @para init_in: input prepare datetime, will compare with first input
        """
        char2ut = {'Y': U.Y, 'm': U.M, 'd': U.D, 'y': U.Y,
                   'H': U.h, 'M': U.m, 'S': U.s, 'z': None,
                   'a': U.D, 'A': U.D, 'b': U.M, 'B': U.M,
                   'c': U.s, 'I': U.h, 'p': U.h, 'u': U.us}
        char2len = {'Y': 4, 'm': 2, 'd': 2, 'H': 2, 'M': 2, 'S': 2, 'y': 2,
                    'z': None, 'a': None, 'A': None, 'b': None, 'B': None,
                    'c': 24, 'I': 2, 'p': 2, 'u': 6}
        self.lst = []
        fmt_i = 0  # last index of fmt append to self.lst
        for match in re.finditer('([%?])(.?)([YmdHMSzaAbBcIpf])', fmt):
            if match.start() != fmt_i:
                self.lst.append(fmt[fmt_i:match.start()])
            skip_on = match.group(1) == '?'
            pad = match.group(2)
            char = match.group(3)
            n = char2len[char] if pad != '' else 0
            ut = char2ut[char]
            self.lst.append(group(pad, n, ut, skip_on))
            fmt_i = match.end()
        if init_in is not None:
            self.last = init_in
        else:
            self.last = datetime(1, 1, 1)

    def _max_diff(self, in_x):
        names = ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
        n = -1
        for i, name in enumerate(names):
            if getattr(self.last, name) != getattr(in_x, name):
                n = i
                break
        return n

    def _output_lst(self, n, in_x):
        ut2name = {U.Y:'year', U.M:'month', U.D:'day',
                   U.h:'hour', U.m:'minute', U.s:'second', U.us:'microsecond'}
        first_ut = [U.Y, U.M, U.D, U.h, U.m, U.s][n]   # first unit in output
        ret = ''
        for x in self.lst:
            if isinstance(x, str):
                ret += x
            elif isinstance(x, group):
                name = ut2name[x.ut]
                if x.skip_on and x.ut.value < first_ut.value:
                    ret += x.spaces
                else:
                    ret += x.format(getattr(in_x, name))
        return ret

    def strftime(self, in_x, update=True):
        n = self._max_diff(in_x)
        if update:
            self.last = in_x
        return self._output_lst(n, in_x)


# tests
if __name__ == "__main__":
    mts = MTshort('? Y/? m/? d % H:%0M:%0S.%6u')
    datis = [datetime(2020, 11, 12, 0, 49, 5),
             datetime(2020, 11, 13, 0, 49, 5),  # test day change
             datetime(2020, 11, 13, 0,  1, 5),  # test invest
             datetime(2021, 11, 13, 1,  1, 5),  # test year change
             datetime(2020, 11, 13, 3,  1, 5),
             datetime(2020, 11, 13, 3,  1, 5)]  # test same
    for dati in datis:
        print(mts.strftime(dati))
