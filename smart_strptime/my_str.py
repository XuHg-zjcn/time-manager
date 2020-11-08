import re
from enum import Enum
from collections import Iterable
from my_lib import udict, oset

re_num = re.compile(r'\d+')
re_eng = re.compile(r'[a-zA-Z]+')
re_norm = re.compile(r'[-:,/ ]+')
re_ext = re.compile(r'^[a-zA-Z]*\.?')

nums = '0123456789'
engs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.'
norms = r'-:.,/\ '
sType = Enum('sType', 'num eng norm other')
StrUsed = Enum('IsUsed', 'unused partused allused')
sType2exam = {sType.num: nums,   sType.eng: engs,   sType.norm: norms}
sType2re_c = {sType.num: re_num, sType.eng: re_eng, sType.norm: re_norm}


class Part:
    """Part for date and time.

    a Part of str, can add to BigPart or unused_parts set
    span: the range of part in main str
    mstr: the main str object
    stype: Enum of sType
    value: int or float value
    flags: flags in running
    """

    def __init__(self, mstr, span: tuple, stype=None, value=None):
        self.span = span
        self.mstr = mstr
        self.stype = self.check_stype(stype)
        self.value = self.get_value(value)
        self.flags = set()

    def part_str(self):
        """Slice main str by span."""
        return self.mstr.in_str[self.span[0]:self.span[1]]

    def check_stype(self, stype):
        """Check input stype is correct.

        @para sType: reference stype
        @raise RuntimeError: stype via detect and input is not same
        @return: sType via detect, and same with input
        """
        s = self.part_str()
        gstype = None
        for key in sType2exam:                            # detce first char
            if s[0] in sType2exam[key]:
                gstype = key
                break
        if len(s) >= 2 and s[0] == '.' and s[1] in nums:  # detct float number
            gstype = sType.num
        for c in s[1:]:                                   # check others char
            if c not in sType2exam[gstype]:
                raise RuntimeError('check_stype faild {},\n{}'
                                   .format(gstype, self.mstr.mark(self.span)))
        assert gstype is not None
        if stype is not None and stype != gstype:
            raise RuntimeError('stype:{} != gstype:{}\n{}'
                               .format(stype, gstype,
                                       self.mstr.mark(self.span)))
        return gstype

    def get_value(self, v):
        """Get the value in part str.

        @para v: defalut value if value can't found.
        @return: the get value result, add to obj attr.
        """
        s = self.part_str()
        if v == 'no find':
            value = None
        elif self.stype == sType.num:
            if s[0] == '.':
                value = float(s)
            else:
                value = int(s)
            if v is not None:
                assert value == v
        else:
            value = v
        return value

    def __str__(self):
        """Generate string for Part print.

        Example:
        -------
        span=(3, 6), str="123", value=123
        """
        if type(self.value) in (int, float) or self.value is None:
            str_value = str(self.value)
        else:
            raise ValueError("self.value isn't int, float or None")
        ret = 'span={:>7}, str="{}", value={}'\
              .format(str(self.span), self.part_str(), str_value)
        return ret

    def __eq__(self, other):
        """Is Part object same.

        according of compare is has same main str and span
        """
        return self.mstr == other.mstr and \
               self.span == other.span

    def __lt__(self, other):
        """Compare parts other at self's right."""
        return self.span[1] <= other.span[0]

    def __gt__(self, other):
        """Compare parts other at self's left."""
        return other.span[1] <= self.span[0]

    def __len__(self):
        """Length of part string."""
        return self.span[1] - self.span[0]

    def __iter__(self):
        """Get iter conv as tuple."""
        return self.span.__iter__()

    def set_str_used(self):
        """Set part str used flags each character in main str."""
        self.mstr.set_str_used(self.span)


class BigPart(dict):
    """Part date(YMD) or time(HMD), can include sub part.

    super class is dict
    dict's key: sType.norm or UType.xxx
    dict's value: Part object

    mstr:  the main str object
    name:  name of BigPart, can be 'date' or 'time'
    span:  all subparts common span
    key_allow: allow key's add to dict, if key not in, will raise KeyError
    norms: normal char parts list
    """

    def __init__(self, mstr, name, key_allow):
        super().__init__()
        self.mstr = mstr
        self.name = name
        self.span = None
        self.key_allow = key_allow
        self.norms = []

    def __setitem__(self, ut, part):
        """Add part obj to BigPart.

        same key only allow setitem once
        @para UType: dict's key
        @para part: part want to add
        @raise KeyError: key 'ut' is not allow or already in dict
        """
        assert isinstance(part, Part)
        if ut != sType.norm:
            # check key is allow
            if ut not in self.key_allow:
                raise KeyError('key {} is invalid for BigPart {}'
                               .format(ut, self.name))
            # check key is free
            if ut in self:
                raise KeyError('key {} is already in BigPart {} dict'
                               .format(ut, self.name))
            super().__setitem__(ut, part)
        else:  # normal char
            self.norms.append(part)
        # Part obj in unused_part
        if part in self.mstr.unused_parts:
            self.mstr.unused_parts.remove(part)
        # Part obj is pop from BigPart
        if 'BigPart poped' in part.flags:
            part.flags.remove('BigPart poped')
        else:
            self.mstr.part_set.add(part)
            part.set_str_used()

        # update self.span
        if self.span is None:
            self.span = list(part.span)
        else:
            if part.span[0] < self.span[0]:  # Part's left point over BigPart
                self.span[0] = part.span[0]
            if part.span[1] > self.span[1]:  # Part's right point over BigPart
                self.span[1] = part.span[1]
        if part.value is None:
            part.value = part.get_value(None)

    def pop(self, ut):
        """Pop a part, and add flag, used in time lmr."""
        part = super().pop(ut)
        part.flags.add('BigPart poped')
        return part

    def check_breakpoint(self):
        """Check is not middle broken.

        such as found HH::SS without minute, YYYY//DD without month
        @raise ValueError: found problem
        """
        keys = list(self.keys())
        if len(keys) > 0:
            k_iter = iter(keys)
            k_cls1 = next(k_iter).__class__
            for k in k_iter:
                assert k.__class__ == k_cls1
        else:
            return
        key_v = list(map(lambda x: x.value, keys))             # value of Enum
        key_v.sort()
        if len(key_v) >= 2:
            for i0, i1 in zip(key_v, key_v[1:]):
                if i0+1 != i1:
                    key_n = list(map(lambda x: x.name, keys))  # name of Enum
                    raise ValueError('found keys:{}, but not {}'
                                     .format(key_n, k_cls1(i1)))

    def check_unused_char(self, allow, disallow):
        """Check unused char in BigPart span, and set flag used each character.

        see my_str.check_unused_char
        @para allow:    allow char
        @para disallow: disallow char
        """
        if self.span is not None:
            self.mstr.check_unused_char(allow, disallow, self.span)

    def __str__(self):
        """Generate string for BigPart print.

        Example:
        -------
        -----------------------------------  (output include the line)
        month  :span= (4, 7), str="Nov", value=11
        year   :span= (0, 4), str="2020", value=2020
        """
        if len(self) != 0:
            ret = '-----------------------------------\n'
            for i in self:
                ret += '{:<7}:{}\n'.format(i.name, self[i])
            ret = ret[:-1]
            return ret
        else:
            return 'empty------------------------------'


class My_str:
    """Main str with status.

    in_str:   the input str
    used:     used flags for each character
    disallow_unused_chars: chars disallow in final result
    part_set: all parts in BigPart span set
    unused_parts: all unused(not in any BigPart) parts
    """

    def __init__(self, in_str):
        self.in_str = in_str
        self.used = [False]*len(in_str)         # only modify by set_str_used
        self.disallow_unused_chars = ''
        self.part_set = udict()                     # for two BigPart
        self.unused_parts = udict(subset_names=[])  # for all unused parts obj

    def get_allsType_parts(self, sType2re_c):
        """Search a group re_compile.

        @para sType2re_c: dict {sType: re.compile}
        """
        def get_atype(self, re_comp, stype, filter_used=StrUsed.unused):
            """Find all use re, atype of sub.

            allow found multply
            @para re_comp: re.compile object
            @para stype: type_id for Part object
            @para filter_used: only output unused
            @return: udict obj
            """
            founds = re_comp.finditer(self.in_str)
            ud = udict()
            for i in founds:
                str_used = self.is_str_used(i.span())
                if filter_used is None or str_used == filter_used:
                    part = Part(self, i.span(), stype, value='no find')
                    ud.add(part)
            return ud

        for stype, re_i in sType2re_c.items():
            self.unused_parts.add_subset(
                stype.name, get_atype(self, re_i, stype))

    def mark(self, index, num=1, out_str=True):
        """Mark '^' range below orignal string.

        @para index:   start index or span tuple
        @para num:     num of mark
        @para out_str: is output orignal string

        @raise ValueError: para error
        @raise IndexError: out of range

        @return: output str
        """
        # get range
        if isinstance(index, Iterable) and len(index) == 2:
            num = index[1] - index[0]
            index = index[0]
        elif isinstance(index, int):
            pass
        else:
            raise ValueError('index must len=2 or int')
        # geterate
        ret = ''
        if out_str:
            ret += self.in_str + '\n'
        N_end_space = len(self.in_str)-index-num
        if N_end_space < 0:
            raise IndexError('end of mark out of range')
        ret += ' '*index+'^'*num+' '*N_end_space
        return ret

    def find_strs(self, subs, puls1):
        """Find which sub in in_str.

        allow onlyone sub can find, else raise ValueError
        @para subs: list of subs
        @para err: show when find multipy subs

        @raise ValueError: found multipy

        @return: found Part
        """
        def find_onlyone(self, sub):
            """Find onlyone sub str or not contain.

            @para sub: the sub str
            @return: found index, -1 if not contain
            """
            index = self.in_str.find(sub)
            if index != -1:         # found
                more = self.in_str.find(sub, index+len(sub))
                if more != -1:       # found more
                    raise ValueError('found multipy {} in str'.format(sub))
            return index

        # TODO: check extend
        def extend_word(self, start):
            m = re_ext.match(self.in_str[start:])
            return m.end(0)

        ret = None
        for ni, sub in enumerate(subs):
            index = find_onlyone(self, sub)
            if index != -1:
                stop = index+len(sub)
                stop += extend_word(self, stop)
                span = (index, stop)
                if ret is None:
                    value = ni+1 if puls1 else ni
                    ret = Part(self, span, sType.eng, value=value)
                else:
                    raise ValueError('found multipy in str')
        return ret

    def search(self, re_comp, sta=0, end=None):
        """Search main str using re.complie.

        @para re_comp: re.complie for search
        @para sta: index of start search
        @para end: index of end search

        @ret found: re.Match object
        @ret spans: spans after add start offset
        """
        found = re_comp.search(self.in_str[sta:end])
        if found is None:
            return None, None
        spans = []
        for i in range(found.lastindex+1):
            m_sp = found.span(i)
            sp1 = (m_sp[0]+sta, m_sp[1]+sta)
            spans.append(sp1)
        return found, spans

    def is_str_used(self, span):
        """Get str use status of span."""
        N_used = 0
        for i in range(*span):
            if self.used[i]:
                N_used += 1
        if N_used == 0:
            str_used = StrUsed.unused
        elif N_used == span[1] - span[0]:
            str_used = StrUsed.allused
        else:
            str_used = StrUsed.partused
        return str_used

    # only call in BigPart.__setitem__, pack by Part.set_str_used,
    # and check_unused_char
    def set_str_used(self, span):
        """Set span used each character.

        @raise RuntimeError: has already used char in span
        """
        str_used = self.is_str_used(span)
        if str_used != StrUsed.unused:
            raise RuntimeError('set_str_used has already used char in span\n{}'
                               .format(str_used.name, self.mark(span)))
        for i in range(*span):
            self.used[i] = True

    def check_unused_char(self, allow, disallow, search_span=None):
        """Check unused char, and set used.

        if char'O' in allow or disallow, as the defalut other chars,
        don't add other char if 'O' in str, is invaild
        char not in both allow and disallow, add to disallow for later call.

        if char not in allow or disallow both,
        the char will disable in the next calls.

        @raise ValueError: disallow unused char
        """
        def get_allow_dis_set(allow, disallow):
            """Get allow and disallow set."""
            allow = set(allow)
            disallow = set(disallow)
            assert set.isdisjoint(allow, disallow)
            if 'O' in allow:    # oset: reversal __contains__
                allow = oset(disallow)
            if 'O' in disallow:
                disallow = oset(allow)
            return allow, disallow

        def uu_span(used, sspan):
            """Get unused_span_list: used flag of char is False spans."""
            uuspan_list = []
            last_span = [0, 0]  # i = index of u1
            for u0, u1, i in zip(used[sspan[0]:], used[sspan[0]+1:],
                                 range(sspan[0]+1, len(used))):
                if u0 and not u1:   # u0 used, u1 not used, as start of span
                    last_span[0] = i
                if not u0 and u1:   # u0 not used, u1 used, as end of span
                    last_span[1] = i
                    uuspan_list.append(tuple(last_span))
            return uuspan_list

        def check_and_set_used(self, uuspan_list, allow, dis):
            for span in uuspan_list:
                if span[1] - span[0] != 1:
                    raise ValueError('multiply unused char continuous\n{}'
                                     .format(self.mark(span)))
                else:
                    i = span[0]
                    assert span[1] == i+1
                    c = self.in_str[i]
                    if c in allow:
                        self.set_str_used(span)
                    elif c in dis:
                        raise ValueError('in call disallow unused char\n{}'
                                         .format(self.mark(i)))
                    elif c in self.disallow_unused_chars:
                        raise ValueError('in My_str disallow unused char\n{}'
                                         .format(self.mark(i)))
                    else:
                        # disable for later calls
                        self.disallow_unused_chars += c

        if search_span is None:
            search_span = (0, len(self.in_str))
        allow, dis = get_allow_dis_set(allow, disallow)
        uuspan_list = uu_span(self.used, search_span)
        check_and_set_used(self, uuspan_list, allow, dis)
        # check and set_str_used

    def print_str_use_status(self, mark):
        """Print main str use status.

        print mark symbol each used char, and count
        @para mark: mark char, 'v' or '.' will above str, '^' will below str

        Example:
        -------
             vvvvvvvvv
        str:|2020.11.7|
        str use status: total=9, used=9, unused=0
        """
        assert mark in {'^', 'v', '.'}
        marks = ''
        n_used = 0
        for used_i in self.used:
            marks += {False: ' ', True: mark}[used_i]
            n_used += used_i
        len_str = len(self.in_str)
        unused = len_str - n_used
        if mark == '^':
            print('str:|{}|\n     {}'.format(self.in_str, marks))
        else:
            print('     {}\nstr:|{}|'.format(marks, self.in_str))
        print('str use status: total={}, used={}, unused={}'
              .format(len_str, n_used, unused))
