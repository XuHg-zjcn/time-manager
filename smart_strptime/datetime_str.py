import datetime                                        # L0 built-in model
from .my_str import sType2re_c2          # L2
from .basetime import UType, Char2UType  # L3 basetime define
from .lmrTime_str import lmrTime_str     # L4 time search type
from .Date_str import Date_str
# level of the module is L5, can use outside package

d_t = '\033[36m'  # datetype
end = '\033[0m'   # end of style


class DateTime_str(lmrTime_str, Date_str):
    r"""Smart time str to datetime (strptime).

    pseudo-code:
    find ll:mm:rr.ss, english
    find YYYYMMDD
    if time_found or flags.find_date42:
        find YYYY, MMDD
        find DD, if onlyone num
    if any about date found:
        set_time_p(n2v='hour')
    else:
        set_time_p(n2v=default_n2v)
    check result
    as datetime object

    part add rule:
        BigPart no breakpoint,           exam: YYYY//DD without month
        limted use spilt char,           time':', date'-./\ ' BigPart',T'
        Parts no overlapped on str,      each char of in_str has flag
        two BigPart not overlapped,      exam: YYYY/MM hh:mm:ss DD
        a Part can only add to a BigPart
        Parts in BigPart are not repeating
    """

    def __init__(self, in_str, fd642=True, dn2v='hour', YY2=True):
        super().__init__(in_str)
        # self.flags 'time_found', 'fd642', 'YY2', 'process OK'
        self.para = {'dn2v': dn2v}  # default time format
        if fd642:
            self.flags.add('fd642')  # find 6,4,2 digts without time found
        if YY2:
            self.flags.add('YY2')    # allow 19YY or 20YY

    def process_check(self):
        """Call after init."""
        assert 'process OK' not in self.flags  # not entry before
        self._process()
        self._check()
        self.flags.add('process OK')

    def _process(self):
        """Process input str."""
        self._time_lmrs()
        self._get_AMPM()

        self._english_month_weekday()
        self._get_allsType_parts(sType2re_c2)
        self._find_date(8)         # find YYYYMMDD
        if ('time_found' in self.flags) or ('fd642' in self.flags):
            self._find_date(4)     # find YYYY, MMDD
            self._find_date(6)     # find YYYYMM, YYMMDD

        fmt_base = ['YMD', 'DMY']
        if 'time_found' in self.flags:
            fmt_base += ['MD']
        else:
            fmt_base += ['MD', 'YM']

        self._unused_chooise(fmt_base)
        self.__onlyone_unused_num_as_day()

        if len(self.date_p) > 0:  # any about date found
            lmrTime_str.set_time_p(self, 'hour')
        else:
            lmrTime_str.set_time_p(self, self.para['dn2v'])

    def _check(self):
        """Check process result."""
        if len(self.date_p) + len(self.time_p) == 0:
            raise ValueError('datetime not found any item')
        date_skips = {UType.Nweek.value, UType.weekday.value}
        self.date_p.check_breakpoint(date_skips)
        self.time_p.check_breakpoint()
        # TODO: check time_p
        self.__check_bigparts_not_overlapped()
        self.date_p.check_unused_char('-./ ', 'O')
        self.time_p.check_unused_char(' ', 'O')
        self.check_unused_char(' ', ':-./')
        super()._check()

    def __onlyone_unused_num_as_day(self):
        """Unused num onlyone, set it to day."""
        nums = self.unused_parts.subset['num']
        if len(nums) == 1:
            oouu = list(nums)[0]
            self.date_p[UType.day] = oouu

    def __check_bigparts_not_overlapped(self):
        """Raise Error if overlapped."""
        if len(self.date_p) >= 1 and len(self.time_p) >= 1:
            date_time = self.date_p.span[1] <= self.time_p.span[0]
            time_date = self.time_p.span[1] <= self.date_p.span[0]
            if not (date_time or time_date):
                raise ValueError('date and time bigparts has overlapped\n\
str :{}\ndate:{}\ntime:{}'.format(self.in_str,
                                  self.mark(self.date_p.span, out_str=False),
                                  self.mark(self.time_p.span, out_str=False)))

    def as_datetime(self):
        """Convert self to datetime object.

        fill today if (year, month, day) items not found
        @raise ValueError: vaild item less than 2
        @raise ValueError: weekday incorrect
        """
        def get_dt_paras(date_p, time_p):
            """Convert date_p and time_p to dt_paras."""
            dt_paras = [None]*7    # temp for datetime paras  YMD,hms,us
            d = {}                 # key:UType, value:Part obj
            d.update(date_p)
            d.update(time_p)
            # fill d(dict) into l(datetime para list), key in both d and dx
            dks = set.intersection(set(d.keys()), set(UT2num.keys()))
            for k in dks:
                dt_paras[UT2num[k]] = d[k].value
            # subsec*1000000 to microsec int
            if U.subsec in d:
                dt_paras[6] = int(d[U.ss].value*1e6)
            # AM or PM found
            if U.ampm in d:
                if d[U.ampm].value == 1:
                    dt_paras[3] += 12
            return d, dt_paras

        def get_nNone_and_fill(dt_paras, today):
            """Get index range of value not None.

            start fill today paras, if None
            """
            # get start of not None item
            s = 0
            while dt_paras[s] is None and s < 3:
                s += 1
            # get end of not None item
            e = s
            while dt_paras[e] is not None and e < 6:
                e += 1
            if e - s < 2:
                raise ValueError('vaild item less than 2:\n{}'
                                 .format(dt_paras))
            for i in range(s):
                dt_paras[i] = today[i]
            return s, e

        U = UType
        UT2num = {U.Y: 0, U.M: 1, U.D: 2, U.h: 3, U.m: 4, U.s: 5}
        today = datetime.date.today()
        today = [today.year, today.month, today.day]

        d, dt_paras = get_dt_paras(self.date_p, self.time_p)
        nNs, nNe = get_nNone_and_fill(dt_paras, today)
        while len(dt_paras) > nNe:  # pop last None items
            dt_paras.pop()

        # TODO: create date obj, if only date found
        dt_obj = datetime.datetime(*dt_paras)  # create datetime obj
        # raise if weekday incorrect
        if U.weekday in d and d[U.WD].value != dt_obj.weekday():
            raise ValueError('weekday in str is {}, but infer by date is {}'
                             .format(d[U.WD].part_str(),
                                     dt_obj.strftime('%Y-%m-%d %A')))
        return dt_obj

    def _unused_chooise(self, formats):
        """Unused numbers add to date BigPart.

        fig1:
        -------
            D  M  Y-<      formats
            Y  M  D |
        n1 =|--|--|-^
        n2 ____|  |
        n3 _______|

        ^
        |
        date_p parts
        unused_parts.subset['num']

        fig2:
        --------
         0   1  2  3  4
        left         right
        [//][ ][ ][ ][//]
            |---lr---|     lr=(1,4) lenlr=4-1=3
             ^  ^  ^
             |  |  |
             n1 n2 n3      Nplr=len([n1,n2,n3...])
        n* are Part obj
        [n1,n2,n3].sort()
        """

        def get_fmt2lrd(formats):
            fmt2lrd = {}            # key: format str, value: lr_dict
            for fmt in formats:      # a format         'YMD'
                lr_d = lr_dict()   # key: UType, value: Part obj
                for c in fmt:        # a char of format 'Y'
                    ut = Char2UType[c]
                    # fill ut_parts
                    if ut in self.date_p:
                        lr_d[ut] = self.date_p[ut]
                    else:
                        lr_d[ut] = None
                fmt2lrd[fmt] = lr_d
            return fmt2lrd

        def remove_unmatched_format(fmt2lrd):
            """ 0   1    2    ni
               [Y] [M]  [D]   format
                |        |    links, linked item in lr_d not None
            p0 p1 p2 p3 p4    parts in merge bigpart
             0  1  2  3  4    bp_ni
            """
            rm_fmt = set()
            bp_merge = self.date_p.copy()
            bp_merge.update(self.time_p)
            bp_merge = list(bp_merge.items())
            for fmt, lr_d in fmt2lrd.items():
                bp_i = None
                for i, (lr, part) in enumerate(lr_d.items()):
                    if bp_i is not None:
                        bp_i += 1  # increase when bp_i assiged
                    if bp_i is None and part is not None:
                        bp_i = i   # init bp_i
                    if bp_i is not None and part is not None:
                        if bp_i >= len(bp_merge):
                            rm_fmt.add(fmt)    # bp_merge not enough
                            continue
                        bp_part = bp_merge[bp_i][1]
                        if part != bp_part:
                            rm_fmt.add(fmt)    # part not same
                            continue
            for i in rm_fmt:
                fmt2lrd.pop(i)

        def get_OK_fmts(fmt2lrd):
            """Find unused parts can push location.

            if any push range of unused part can't found, remove the format
            from fmt2lrd.

            OK_fmts:
            -------
            {fmt1: {lr:part_lr, lr:part_lr}, format1
             fmt2: {lr:part_lr, lr:part_lr}, format2
             fmt3: {lr:part_lr, lr:part_lr}} format3
            """
            def find_range_can_push(lr_d, part_obj):
                lr = lr_d.get_allow_lr(part_obj)  # l<=x<=r, lr_d[x] are None
                if lr is None:
                    return None
                else:
                    li, ri = lr
                    Left = lr_d.next_None(li, prev_next=1)      # [Left, Right)
                    Right = lr_d.next_None(ri, prev_next=-1)+1  # Right+1
                    return Left, Right
            rm_fmt = set()
            OK_fmts = {}
            for fmt, lr_d in fmt2lrd.items():
                skip = False    # append in rm_i
                ok_fills = {}   # lr -> [part_lr, ...]
                for uup in self.unused_parts.subset['num']:
                    lr = find_range_can_push(lr_d, uup)
                    if lr is None:
                        rm_fmt.add(fmt)
                        skip = True
                        break
                    else:
                        if lr not in ok_fills:
                            ok_fills[lr] = []
                        ok_fills[lr].append(part_lr(fmt, uup, lr))
                if skip:
                    continue
                else:
                    OK_fmts[fmt] = ok_fills
            for i in rm_fmt:    # remove find push range faild
                fmt2lrd.pop(i)
            return OK_fmts

        def remove_lenlr_neq_Nplr(OK_fmts):
            # remove if len(lr) != num of part_lr, see fig2
            rm_fmt = set()
            for fmt, d_lr2plr in OK_fmts.items():
                for lr, plrs in d_lr2plr.items():
                    dlr = lr[1]-lr[0]
                    n_plr = len(plrs)
                    if dlr != n_plr:
                        rm_fmt.add(fmt)
            for i in rm_fmt:
                OK_fmts.pop(i)

        def fill_myOD(self, ok_fills, myOD):
            mr_dict = mrange_dict(ok_fills)
            mr_dict.fill(self.date_p, myOD)

        def onlyone_fmt_fill(self, OK_fmts):
            fmt = list(OK_fmts.keys())[0]
            ok_fills = list(OK_fmts.values())[0]
            myOD = fmt2lrd[fmt]
            fill_myOD(self, ok_fills, myOD)

        def order_format_fill(self, OK_fmts, orders=formats):
            assert len(OK_fmts) > 1
            fmts = list(OK_fmts.keys())
            order_i = min(map(lambda x: orders.index(x), fmts))
            fmt_first = orders[order_i]
            ok_fills = OK_fmts[fmt_first]
            myOD = fmt2lrd[fmt_first]
            fill_myOD(self, ok_fills, myOD)

        fmt2lrd = get_fmt2lrd(formats)
        remove_unmatched_format(fmt2lrd)  # remove in fmt2lrd
        OK_fmts = get_OK_fmts(fmt2lrd)
        remove_lenlr_neq_Nplr(OK_fmts)     # remove in OK_fmts
        if len(OK_fmts) == 0:
            return
        elif len(OK_fmts) == 1:
            onlyone_fmt_fill(self, OK_fmts)
        else:
            order_format_fill(self, OK_fmts, formats)

    def __repr__(self):
        ret = ''
        ret += self.str_use_status('v')
        ret += '{}date:{}{}\n'.format(d_t, end, repr(self.date_p))
        ret += '{}time:{}{}'.format(d_t, end, repr(self.time_p))
        return ret


class lr_dict(dict):
    def __init__(self):
        super().__init__()
        self.klst = []

    def __setitem__(self, k, v):
        if isinstance(k, int):    # k as index
            assert k < len(self.klst)
            k = self.klst[k]
        if k not in self:
            self.klst.append(k)
        super().__setitem__(k, v)

    def __getitem__(self, k):
        if isinstance(k, int):    # k as index
            k = self.klst[k]
        return super().__getitem__(k)

    def get_allow_lr(self, part_obj):
        '''
        prev left ... right next
                part_obj

        prev and next are not None
        prev.end <= part_obj.start   and   part_obj.end <= next.start
        left = prev+1
        right = next-1

        part_obj can add to left<=x<=right
        '''
        left = 0
        right = len(self.klst) - 1
        for ni, k in enumerate(self.klst):
            part_i = self[k]
            if part_i is not None:
                if part_i < part_obj:
                    left = ni + 1   # prev = v
                if part_i > part_obj:
                    right = ni - 1  # next = v
                    break
        if left > right:
            return None
        return left, right

    def next_None(self, ki, prev_next):
        Nlen = len(self.klst)
        ki = {1: 0, -1: Nlen-1}[prev_next] if ki is None else ki
        sli = {1: (ki, Nlen, 1), -1: (ki, -1, -1)}[prev_next]
        for i in range(*sli):
            if self[self.klst[i]] is None:
                return i
        return sli[1]-prev_next

    def pop():                    # don't delete item
        raise NotImplementedError('my_odict delete is forbidden')


class part_lr:
    def __init__(self, fmt, part, lr):
        self.fmt = fmt
        self.part = part
        self.lr = lr
        self.l = lr[0]
        self.r = lr[1]

    def __lt__(self, other):
        if max(self.l, other.l) > min(self.r, other.r):
            raise RuntimeError('part_lr overlapped')
        return self.l <= other.l or self.r <= other.r


class mrange_dict(dict):  # dict[Part.tuple] = [plr1, plr2]
    def __init__(self, from_dict):
        super().__init__(from_dict)

    def fill(self, date_p, my_odict):
        for lr, plrs in self.items():  # a space can fill
            if lr[1] - lr[0] == len(plrs):
                cp_plrs = plrs.copy()
                cp_plrs.sort(key=lambda x: x.part)  # part
                ut_i = lr[0]
                for plr in cp_plrs:
                    date_p[my_odict.klst[ut_i]] = plr.part
                    ut_i += 1
