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


class MTshort:
    """Get strftime with clear same part.

    compare to last input, find biggest different part, the before part will to
    spaces ' ', after and the part will keep.

    however complete time will keep output.
    if biggest different part is day, month will also keep.
    """

    unit_level = [U.Y, U.M, U.D, U.h, U.m, U.s, U.us]

    def __init__(self, fmt='%Y/%m/%d %H:%M:%S', init_in=None):
        """Init MTshort object.

        @para fmt: strftime format string, can't change after create
        @para init_in: input prepare datetime, will compare with first input
        """
        char2ut = {'Y': U.Y, 'm': U.M, 'd': U.D, 'y': U.Y,
                   'H': U.h, 'M': U.m, 'S': U.s, 'z': None,
                   'a': U.D, 'A': U.D, 'b': U.M, 'B': U.M,
                   'c': U.s, 'I': U.h, 'p': U.h, 'f': U.us}
        char2len = {'Y': 4, 'm': 2, 'd': 2, 'H': 2, 'M': 2, 'S': 2, 'y': 2,
                    'z': None, 'a': None, 'A': None, 'b': None, 'B': None,
                    'c': 24, 'I': 2, 'p': 2, 'f': 6}
        self.fmt = fmt
        self.levels = []  # level of each item
        ulens = []        # len span of each item in output
        fmt_p = [0]       # span of each strftime item in output
        for match in re.finditer('%([YmdHMSzaAbBcIpf])', fmt):
            char = match.group(1)

            level = MTshort.unit_level.index(char2ut[char])
            self.levels.append(level)

            ulen = char2len[char]
            ulens.append(ulen)

            msp = match.span(0)   # span in strftime format str
            fmt_p += msp          # append start and end

        last_oi = 0  # index in output str
        self.o_spans = []
        for prev_b, a, b, ul in zip(fmt_p[0::2], fmt_p[1::2], fmt_p[2::2], ulens):
            last_oi += a - prev_b
            o_a = last_oi
            last_oi += ul
            o_b = last_oi
            self.o_spans.append((o_a, o_b))
        self.last = [datetime.now().year, 0, 0, 0, 0, 0, 0]
        if init_in is not None:
            self.update(init_in)

    def _clear_output(self, time_str, ret_max_unit):
        """Clear output string over max unit.

        over max unit item will be space ' '
        @para time_str: orignail strftime str
        @para ret_max_unit: keep max unit, index of MTshort.unit_level
        @ret time_str: processed strftime str
        """
        osp_s = []
        for i, level in enumerate(self.levels):
            if level < ret_max_unit:  # unit index small, unit big
                osp = self.o_spans[i]
                osp_s.append([i, i, osp[0], osp[1]])  # first i keep
        if len(osp_s) == 0:                         # second i change in merge
            return time_str
        elif len(osp_s) == 1:  # only one span, no need merge
            osp_s2 = osp_s
        else:
            # merge spans, clear char between item
            osp_s2 = [osp_s[0]]
            for osp in osp_s[1:]:
                if osp_s2[-1][1]+1 == osp[1]:  # next is near prev
                    osp_s2[-1][1] = osp[1]     # change index
                    osp_s2[-1][3] = osp[3]     # merge span
                else:
                    osp_s2.append(osp)
        for osp in osp_s2:        # extend output clear span
            i_prev = osp[0] - 1   # extend start
            if i_prev >= 0:
                osp[2] = self.o_spans[i_prev][1]
            i_next = osp[1] + 1   # extend end
            if i_next < len(self.o_spans):
                osp[3] = self.o_spans[i_next][0]
        for osp in osp_s2:
            olen = osp[3] - osp[2]     # set output item charaters to space
            time_str = time_str[:osp[2]] + ' '*olen + time_str[osp[3]:]
        return time_str

    def _get_max_unit(self, in_x, names):
        last_same = 3    # show full time
        ulst = []
        for ni, unit in enumerate(names):
            inxx_u = getattr(in_x, unit)
            ulst.append(inxx_u)
        for i, (last_u, inxx_u) in enumerate(zip(self.last, ulst)):
            if last_u != inxx_u:
                last_same = i
                break
        if last_same >= 3:   # must show full time
            max_unit = 3
        elif last_same == 2:
            max_unit = 1  # no show only day,  with month
        else:
            max_unit = last_same
        return ulst, max_unit

    def strftime(self, in_x, update=True):
        """Get datetime strftime with clear same part.

        @para in_x: datetime, time.struct_time or timestramp
        @para update: is update for next compare, false will keep current
        @return: cleaned time string
        """
        dati_names = ['year', 'month', 'day',
                      'hour', 'minute', 'second']
        tm_time_names = ['tm_year', 'tm_mon', 'tm_mday',
                         'tm_hour', 'tm_min', 'tm_sec']
        if isinstance(in_x, datetime):                       # datetime
            time_str = in_x.strftime(self.fmt)
            ulst, ret_max_unit = self._get_max_unit(in_x, dati_names)
        elif isinstance(in_x, time.struct_time):             # time.struct_time
            time_str = time.strftime(self.fmt, in_x)
            ulst, ret_max_unit = self._get_max_unit(in_x, tm_time_names)
        elif isinstance(in_x, int) or isinstance(in_x, float):  # timestamp
            dati_obj = datetime.fromtimestamp(in_x)
            time_str = dati_obj.strftime(self.fmt)
            ulst, ret_max_unit = self._get_max_unit(dati_obj, dati_names)
        # get original time str
        time_str = self._clear_output(time_str, ret_max_unit)
        if update:
            self.last = ulst
        return time_str


# tests
if __name__ == "__main__":
    mts = MTshort('%Y/%m/%d %H:%M:%S')
    datis = [datetime(2020, 11, 12, 0, 49, 5),
             datetime(2020, 11, 13, 0, 49, 5),  # test day change
             datetime(2020, 11, 13, 0,  1, 5),  # test invest
             datetime(2021, 11, 13, 1,  1, 5),  # test year change
             datetime(2020, 11, 13, 3,  1, 5),
             datetime(2020, 11, 13, 3,  1, 5),  # test same
             time.gmtime(1605205991.23),   # invaild %f in time.struct_time
             1605205993.5759933,           # test timestamp float
             1605205993]                   # test timestamp int
    for dati in datis:
        print(mts.strftime(dati))
