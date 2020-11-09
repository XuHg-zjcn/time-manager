#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta
import re

from my_str import Part, BigPart, My_str
from time_str import Time_str
from time_str import UType, UxType, sType
from my_lib import udict
from my_lib import strictly_increasing

def re_comp_unit(name_spilt, allow_s=True):
    """Get re.compile for time_unit

    @para name_spilt: parts of name,  example: ('h', 'our')
    @para allow_s: is allow append 's' after unit, should off in 'ms', 'us'...

    re_template:
    --------
    ignore capital, {0} unit name, {1} 's?' or ''(empty)
    can space charater bettwen number and unit
    if number not found, only match unit
    number allow float
    """
    re_template = r'(?i)(\d+(\.\d)?)\s{{0,2}}({0}{1})'
    ext = r'{0}({1})?'  # {0}:first letter, {1}:other letter
    def N_ext(lst):
        if len(lst) == 1:
            return lst[0]
        else:
            return ext.format(lst[0], N_ext(lst[1:]))

    assert 1 <= len(name_spilt) <= 3
    s = {False: '', True: 's?'}[allow_s]
    re_str = re_template.format(N_ext(name_spilt), s)
    return re.compile(re_str)

U = UType
units = {U.year  : ('y', 'ear'), 
         U.month : ('m', 'onth'),
         U.Nweek : ('w', 'eek'),
         U.day   : ('d', 'ay'),
         U.hours : ('h', 'our'),
         U.minute: ('m', 'in', 'ute'),
         U.second: ('s', 'ec', 'ond'),
         U.ms    : ('ms',)}
del U

ut2re_c = {}
for ut, spilt in units.items():
    allow_s = len(spilt) != 1  # no 's' after 'ms'
    ut2re_c[ut] = re_comp_unit(spilt, allow_s)


class Timedelta_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)

    def process(self):
        """Process input str."""
        self.t_units = BigPart(self, 't_units', units.keys())
        self.time_p = BigPart(self, 'time', UxType['lmrTime'])
        self.time_lmrs()
        mxx = self.find_units(ut2re_c)
        self.unused_parts.add_subset('mxx', mxx)
        if len(mxx) > 0:
            self.month_or_minute(mxx)
        if 'time_found' in self.flags:
            n2v = self.get_n2v()
            self.set_time_p(n2v)

    def check(self):
        is_inc, cp = self.check_inc()

    def time_lmrs(self):
        """See time_str.Time_str.time_lmrs."""
        Time_str.time_lmrs(self)

    def set_time_p(self, n2v=None):
        """See time_str.Time_str.set_time_p."""
        Time_str.set_time_p(self, n2v)

    def find_units(self, ut2re_c):
        mxx = udict(check_add=False)
        for ut, re_c in ut2re_c.items():
            _, sp = self.search(re_c)
            if sp is not None:
                part = Part(self, sp[0], sType.num, sp[1])
                if ut in {UType.month, UType.minute} and sp[3].len_ab() == 1:
                    mxx.add(part)
                else:
                    self.t_units[ut] = part
        for m in mxx:
            if m in self.part_set:
                mxx.remove(m)
        return mxx

    def check_inc(self):
        cp = list(self.t_units.items())
        cp.sort(key=lambda x: x[1])                    # sort by Part
        ut_v = map(lambda x: x[0].value, cp)           # get UType Enum values
        ut_v = list(ut_v)                              # Enum values to list
        is_inc = strictly_increasing(ut_v)
        return is_inc, cp

    def month_or_minute(self, mxx):
        def use_sort(check_inc_result, mxx):
            is_inc, cp = self.check_inc()
            if not is_inc:
                raise ValueError('unit order incorrect')
            cp += list(map(lambda x: (None, x), mxx.values()))
            cp.sort(key=lambda x: x[1])                    # sort by Part
            # get None item with index
            v_N = filter(lambda x: x[1][0] is None, enumerate(cp))
            v_N = list(v_N)
            for ni, (_, part) in v_N:
                if ni+1 < len(cp) and cp[ni+1][0].value > UType.month.value:
                    self.t_units[UType.month] = part
                elif ni-1 >= 0 and cp[ni-1][0].value < UType.minute.value:
                    self.t_units[UType.minute] = part
            return mxx

        def score_set(bp_keys):
            U = UType
            month_set = {U.year, U.day, U.Nweek}
            minute_set = {U.hours, U.second, U.ms}
            month_score = len(set.intersection(month_set, bp_keys))
            minute_score = len(set.intersection(minute_set, bp_keys))
            if month_score == minute_score:
                raise ValueError('month or minute')
            elif month_score > minute_score:  # month higher score
                assert U.ms not in bp_keys
                return U.month
            elif month_score < minute_score:  # minute higher score
                assert U.year not in bp_keys
                return U.minute

        if len(mxx) == 0:
            return
        mxx = use_sort(self.check_inc(), mxx)
        if len(mxx) == 1:
            ut = score_set(self.t_units.keys())
            part = list(mxx.values())[0]
            self.t_units[ut] = part
        assert len(mxx) == 0

    def get_n2v(self, default='hours'):
        if len(self.t_units) > 0:
            bp_keys = self.t_units.keys()
            bp_kv = list(map(lambda x:x.value, bp_keys))
            kv_max = max(bp_kv)
            kv_min = min(bp_kv)
            if kv_min > UType.day.value:  # Enum value
                raise ValueError('time lmr found and \
                                 little than day item found')
            if kv_min <= UType.day.value:
                n2v = 'hours'
            else:
                n2v = 'second'
        else:
            n2v = default
        return n2v

def test():
    test_ok = ['1d 12:10', '1d 12:14', '12:34:12', '12m34s', '1h12m34s']
    test_err = ['1s 12:14']
    dt_str = Timedelta_str('1h12m34s')
    dt_str.process()
    dt_str.print_str_use_status('v')
    print('time_p: ', dt_str.time_p)
    print('t_uints:', dt_str.t_units)
    return dt_str

dt_str = test()
