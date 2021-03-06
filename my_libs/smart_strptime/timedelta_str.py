import re                                 # L0 built-in model
from datetime import timedelta

from .my_lib import udict                 # L1 my_lib
from .my_lib import strictly_increasing
from .my_str import Part, BigPart, sType  # L2 my_str
from .basetime import UType               # L3 basetime define
from .lmrTime_str import lmrTime_str      # L4 time search type
# level of the module is L5, can use outside package

d_t = '\033[36m'  # datetype
end = '\033[0m'       # end of style

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
    re_template = r'(?i)((\d+)?(\.\d+)?)\s{{0,2}}({0}{1})'
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
         U.hour  : ('h', 'our'),
         U.minute: ('m', 'in', 'ute'),
         U.second: ('s', 'ec', 'ond'),
         U.ms    : ('ms',)}
del U

ut2re_c = {}
for ut, spilt in units.items():
    allow_s = len(spilt) != 1  # no 's' after 'ms'
    ut2re_c[ut] = re_comp_unit(spilt, allow_s)


class TimeDelta_str(lmrTime_str):
    def __init__(self, in_str):
        super().__init__(in_str)

    def process_check(self):
        if 'process_check' in self.flags:
            raise RuntimeError('process_check already OK')
        self._process()
        self._check()
        self.flags.add('process_check_ok')

    def _process(self):
        """Process input str."""
        self.t_units = BigPart(self, 't_units', units.keys())
        super().process()
        mxx = self.__find_units(ut2re_c)
        self.unused_parts.add_subset('mxx', mxx)
        if len(mxx) > 0:
            self.__month_or_minute(mxx)
        if 'time_found' in self.flags:
            n2v = self.__get_n2v()
            self.set_time_p(n2v)

    def _check(self):
        if len(self.t_units) + len(self.time_p) == 0:
            raise ValueError('timedelta not found any item')
        self.check_unused_char(' ,', 'O')
        super()._check()

    def __find_units(self, ut2re_c):
        mxx = udict(check_add=False)
        for ut, re_c in ut2re_c.items():
            m, sp = self.search(re_c)
            if sp is not None:
                if m.group(1) == '' or m.group(4) == '':
                    continue
                part = Part(self, sp[0], sType.num, sp[1])
                if ut in {UType.month, UType.minute} and sp[4].len_ab() == 1:
                    mxx.add(part)
                else:
                    self.t_units[ut] = part
        for m in mxx:
            if m in self.part_set:
                mxx.remove(m)
        return mxx

    def __check_inc(self):
        cp = list(self.t_units.items())
        cp.sort(key=lambda x: x[1])                    # sort by Part
        ut_v = map(lambda x: x[0].value, cp)           # get UType Enum values
        ut_v = list(ut_v)                              # Enum values to list
        is_inc = strictly_increasing(ut_v)
        return is_inc, cp

    def __month_or_minute(self, mxx, defalut=UType.minute):
        def use_sort(mxx):
            is_inc, cp = self.__check_inc()
            if not is_inc:
                raise ValueError('unit order incorrect')
            cp += list(map(lambda x: (None, x), mxx.values()))
            cp.sort(key=lambda x: x[1])                    # sort by Part
            # get None item with index
            v_N = filter(lambda x: x[1][0] is None, enumerate(cp))
            v_N = list(v_N)
            utv_month = UType.month.value
            utv_minute = UType.minute.value
            for ni, (_, part) in v_N:
                if ni+1 < len(cp):
                    utv_next = cp[ni+1][0].value
                    if utv_month < utv_next <= utv_minute:
                        self.t_units[UType.month] = part
                if ni-1 >= 0:
                    utv_prev = cp[ni-1][0].value
                    if utv_month <= utv_prev < utv_minute:
                        self.t_units[UType.minute] = part
            return mxx

        def score_set(self, part, tu_keys):
            U = UType
            month_set = {U.year, U.day, U.Nweek}
            minute_set = {U.hour, U.second, U.ms}
            month_score = len(set.intersection(month_set, tu_keys))
            minute_score = len(set.intersection(minute_set, tu_keys))
            if month_score == minute_score:
                return None
            elif month_score > minute_score:  # month higher score
                assert U.ms not in tu_keys
                return UType.month
            elif month_score < minute_score:  # minute higher score
                assert U.year not in tu_keys
                return UType.minute

        if len(mxx) == 0:
            return
        mxx = use_sort(mxx)
        if len(mxx) == 1:
            part = list(mxx.values())[0]
            tu_keys = self.t_units.keys()
            ut = score_set(self, part, tu_keys)
            if ut is not None:
                self.t_units[ut] = part
            else:
                self.t_units[defalut] = part
        assert len(mxx) == 0

    def __get_n2v(self, default='second'):
        if len(self.t_units) > 0:
            bp_keys = self.t_units.keys()
            bp_kv = list(map(lambda x: x.value, bp_keys))
            kv_max = max(bp_kv)
            if kv_max > UType.day.value:  # Enum value, as small as unit big
                raise ValueError('time lmr found and\
 little than day item found')
            else:    # kv_max <= UType.day.value
                n2v = 'second'
        else:
            n2v = default
        return n2v

    def as_timedelta(self):
        def check_disjoint(t_units, time_p):
            tp_k = set(time_p.keys())
            tu_k = set(t_units.keys())
            disjoint = set.isdisjoint(tp_k, tu_k)
            assert disjoint

        def merges(t_units, time_p):
            merge = t_units.copy()
            merge.update(time_p)
            if UType.subsec in merge.keys():
                merge[UType.sec].value += merge[UType.subsec].value
                merge.pop(UType.subsec)
            return merge

        def get_para_dict(merged):
            U = UType
            ut2td = {U.Nweek: 'weeks', U.day: 'days', U.hour: 'hours',
                     U.min: 'minutes', U.sec: 'seconds'}
            is_subset = set(merged.keys()).issubset(set(ut2td.keys()))
            if not is_subset:
                more = merged.keys() - ut2td.keys()
                raise ValueError('datetime.timedelta not allow this units:\n{}'
                                 .format(more))
            paras = {}
            for ut, part in merged.items():
                paras[ut2td[ut]] = part.value
            return paras

        if 'process_check_ok' not in self.flags:
            raise RuntimeError('call as_timedelta before process_check')
        check_disjoint(self.t_units, self.time_p)
        merged = merges(self.t_units, self.time_p)
        paras = get_para_dict(merged)
        return timedelta(**paras)

    def as_sec(self):
        td = self.as_timedelta()
        return td.total_seconds()

    def __repr__(self):
        ret = super().__repr__()
        ret += '{}t_uint:{} {}\n'.format(d_t, end, repr(self.t_units))
        ret += '{}time_p:{} {}\n'.format(d_t, end, repr(self.time_p))
        ret += '-------------------------------------------------\n'
        if 'process_check_ok' in self.flags:
            td = self.as_timedelta()
            ret += '{}time delta:{} {}\n'.format(d_t, end, td)
            sec = td.total_seconds()
            ret += '     {}total:{} {}sec\n'.format(d_t, end, sec)
        return ret[:-1]
