import datetime
import re
from enum import Enum
from my_str import Part, BigPart, My_str
from my_str import sType, sType2re_c
from my_lib import strictly_increasing, my_odict
from my_lib import mrange_dict, part_lr
from my_lib import span

weekday_full = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
weekday_short = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']

month_full = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'Spetember', 'October', 'November', 'December']
month_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Spet','Oct', 'Nov', 'Dec']
ampm = ['AM', 'PM']

eType = Enum('eType', 'weekday month ampm')  # english str part type
fType = Enum('fType', 'full short')          # english str part full or short
# eType and fType to str list, unused
eng_strs = {(eType.weekday, fType.full ): weekday_full,
            (eType.weekday, fType.short): weekday_short,
            (eType.month,   fType.full ): month_full,
            (eType.month,   fType.short): month_short,
            (eType.ampm,    None       ): ampm}

re_lmrs = re.compile(r'(\d+):(\d+:)?(\d+)(\.\d+)?')


class UType(Enum):
    """Time unit type and time lmr.

    full name and short name
    date short name use Capital letter Y, M, M, WD(WeekDay)
    time short name use small letter   ap(Am/Pm), h, m, s
    time lmr short name use            lt,md,rt (LefT, MiDDle, RighT)
    """

    # date
    year = 0
    month = 1
    day = 2
    weekday = 3  # skip in check_breakpoint
    Y = 0
    M = 1
    D = 2
    WD = 3
    # time
    ampm = 4     # skip in check_breakpoint
    hours = 5
    minute = 6
    second = 7
    subsec = 8
    ap = 4
    h = 5
    m = 6
    s = 7
    ss = 8
    # time lmr
    left = 9
    midd = 10
    right = 11
    lt = 9
    md = 10
    rt = 11


def dt(U):
    """Generate UType set and dict."""
    Date = {U.Y, U.M, U.D, U.WD}
    Time = {U.ap, U.h, U.m, U.s, U.ss}
    lmr  = {U.lt, U.md, U.rt}
    lmrT = set.union(Time, lmr)
    UxType = {'Date': Date, 'Time': Time, 'lmr': lmr, 'lmrTime': lmrT}
    Char2UType = {'Y': U.Y, 'M': U.M, 'D': U.D, 'W': U.WD,
                  'p': U.ap,'h': U.h, 'm': U.m, 's': U.s, 'S': U.ss}
    return UxType, Char2UType

UxType, Char2UType = dt(UType)


class Time_str(My_str):
    r"""Smart time str to datetime (strptime).

    pseudo-code:
    find ll:mm:rr.ss, english
    find YYYYMMDD
    if time_found or flags.find_date42:
        find YYYY, MMDD
        find DD, if onlyone num
    if any about date found:
        set_time_p(n2v='hours')
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

    def __init__(self, in_str, fd642=True, default_n2v='hours', YY2=True):
        super().__init__(in_str)
        self.flags = set()  # 'time_found', 'fd642', 'YY2', 'process OK'
        self.para = {'dn2v': default_n2v}  # default time format
        if fd642:
            self.flags.add('fd642')  # find 6,4,2 digts without time found
        if YY2:
            self.flags.add('YY2')    # allow 19YY or 20YY

    def process_check(self):
        """Call after init."""
        assert 'process OK' not in self.flags  # not entry before
        self.date_p = BigPart(self, 'date', UxType['Date'])
        self.time_p = BigPart(self, 'time', UxType['lmrTime'])
        self.process()
        self.check()
        self.flags.add('process OK')
        
    def process(self):
        """Process input str."""
        self.time_lmrs()
        self.english_month_weekday_ampm()
        self.get_allsType_parts(sType2re_c)
        self.find_date(8)         # find YYYYMMDD
        if ('time_found' in self.flags) or ('fd642' in self.flags):
            self.find_date(4)     # find YYYY, MMDD
            self.find_date(6)     # find YYYYMM, YYMMDD
            self.unused_chooise()
            self.onlyone_unused_num_as_day()
        if len(self.date_p) > 0:          # any about date found
            self.set_time_p('hours')
        else:
            self.set_time_p(self.para['dn2v'])

    def check(self):
        """Check process result."""
        self.date_p.check_breakpoint()
        self.time_p.check_breakpoint()
        # TODO: check time_p
        self.check_bigparts_not_overlapped()
        self.date_p.check_unused_char('-./ ', 'O')
        self.time_p.check_unused_char(' ', 'O')
        self.check_unused_char(' ', ':-./')

    def english_month_weekday_ampm(self):
        """find english str"""
        month = self.find_strs(month_short, puls1=True)
        weekday = self.find_strs(weekday_short, puls1=False)
        apm = self.find_strs(ampm, 'AMPM')
        if month is not None:
            self.date_p[UType.month] = month
        if weekday is not None:
            self.date_p[UType.weekday] = weekday
        if apm is not None:
            self.time_p[UType.ampm] = apm

    def find_date(self, digts):
        def num8(self, part, s, e, inti):
            if e-s == 8:
                self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
                self.date_p[UType.month] = Part(self, (s+4, s+6), sType.num)
                self.date_p[UType.day  ] = Part(self, (s+6, e  ), sType.num)
                return True
            return False

        def num6(self, part, s, e, inti):
            def YYYYMM(self, s, e):
                self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
                self.date_p[UType.month] = Part(self, (s+4, e  ), sType.num)

            def YYMMDD(self, s, e):
                self.date_p[UType.year ] = Part(self, (s,   s+2), sType.num)
                self.date_p[UType.month] = Part(self, (s+2, s+4), sType.num)
                self.date_p[UType.day  ] = Part(self, (s+4, e  ), sType.num)

            if e-s == 6:
                if 'YY2' in self.flags:
                    if 191300 <= inti < 210000:  # TODO: add Waring
                        YYYYMM(self, s, e)       # probably not accurate
                    else:
                        YYMMDD(self, s, e)
                else:
                    YYYYMM(self, s, e)
                return True
            return False

        def num4(self, part, s, e, inti):
            if e-s == 4:
                if 1970 <= inti < 2050:
                    self.date_p[UType.year ] = Part(self, (s, e  ), sType.num)
                    return True
                elif 101 <= inti <= 1231:
                    self.date_p[UType.month] = Part(self, (s, s+2), sType.num)
                    self.date_p[UType.day  ] = Part(self, (s+2, e), sType.num)
                    return True
            return False

        nums = self.unused_parts.subset['num']
        for part in nums:
            s = part.span[0]
            e = part.span[1]
            match = part.part_str()
            inti = int(match)

            func = {8: num8, 6: num6, 4: num4}[digts]
            if func(self, part, s, e, inti) is True:
                nums.remove(part)

    def time_lmrs(self):
        """Get time LL:MM:RR.subsec.

        Middle and Subsec can skip.
        """
        m, sp = self.search(re_lmrs)
        if sp is None:
            return
        self.flags.add('time_found')
        # append Parts to self.time_parts
        self.time_p[UType.left] = Part(self, sp[1], sType.num)
        self.time_p[sType.norm] = \
            Part(self, span(sp[1].e, sp[1].e+1), sType.norm)
        # middle item found
        if m.group(2) is not None:
            self.time_p[UType.midd] = \
                Part(self, span(sp[2].s, sp[2].e-1), sType.num)
            self.time_p[sType.norm] = \
                Part(self, span(sp[2].e-1, sp[2].e), sType.norm)

        self.time_p[UType.right] = Part(self, sp[3], sType.num)
        # subsec found
        if m.group(4) is not None:
            self.time_p[UType.subsec] = Part(self, sp[4], sType.num)

    def set_time_p(self, n2v=None):
        """Set time lmrs to hmss.

        ll:mm:rr        -> HH:MM:SS
        ll:mm:rr.sss... -> HH:MM:SS.subsec
              rr.sss... ->       SS.subsec
        ll :  rr.sss... ->    MM:SS.subsec
        ll :  rr          ?-> HH:MM or MM:SS
        @para n2v: if found ll:rr, such as 12:34,
                   'hours' for HH:MM, 'second' for MM:SS, None raise ValueError
        """
        assert 'set_time_p' not in self.flags  # no entry before
        B = UType
        #            src_keys              dst_keys
        dict_rule = {(B.lt, B.md, B.rt      ): (B.h, B.m, B.s      ),
                     (B.lt, B.md, B.rt, B.ss): (B.h, B.m, B.s, None),
                     (            B.rt, B.ss): (          B.s, None),
                     (B.lt,       B.rt, B.ss): (     B.m, B.s, None)}

        def get_src_keys(time_p):
            src_keys = []
            for key in (B.lt, B.md, B.rt, B.ss):
                if key in time_p:
                    src_keys.append(key)
            src_keys = tuple(src_keys)
            return src_keys

        def get_dst_keys(src_keys, dict_rule, n2v):
            # use dict_rule
            if src_keys in dict_rule:
                dst_keys = dict_rule[src_keys]
            # use n2v
            elif src_keys == (B.lt, B.rt):
                if n2v == 'hours':
                    dst_keys = (B.h, B.m)
                elif n2v == 'second':
                    dst_keys = (B.m, B.s)
                else:
                    raise ValueError('n2v must be hours or second')
            # empty src_keys
            elif src_keys == ():
                dst_keys = ()
            else:
                raise KeyError('src_keys {} not match'.format(src_keys))
            return dst_keys

        src_keys = get_src_keys(self.time_p)
        dst_keys = get_dst_keys(src_keys, dict_rule, n2v)
        assert len(src_keys) == len(dst_keys)
        for s_k, d_k in zip(src_keys, dst_keys):
            if d_k is not None:
                self.time_p[d_k] = self.time_p.pop(s_k)  # pop lmr to hms
        self.flags.add('set_time_p')

    def onlyone_unused_num_as_day(self):
        """Unused num onlyone, set it to day."""
        nums = self.unused_parts.subset['num']
        if len(nums) == 1:
            oouu = list(nums)[0]
            self.date_p[UType.day] = oouu

    def check_bigparts_not_overlapped(self):
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
                dt_paras[s] = today[s]
                s += 1
            # get end of not None item
            e = s
            while dt_paras[e] is not None and e < 6:
                e += 1
            if e - s < 2:
                raise ValueError('vaild item less than 2:\n{}'
                                 .format(dt_paras))
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

    def unused_chooise(self, formats=['YMD', 'DMY', 'YM']):
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
        def find_range_can_push(my_od, part_obj):
            lr = my_od.get_allow_lr(part_obj)
            if lr is None:
                return None
            else:
                li, ri = lr
                Left = my_od.next_None(li, prev_next=1)      # [Left, Right)
                Right = my_od.next_None(ri, prev_next=-1)+1  # Right+1
                return Left, Right

        def get_fmt2myOD(formats):
            fmt2myOD = {}            # key: format str, value: my_odict
            for fmt in formats:      # a format         'YMD'
                my_od = my_odict()   # key: UType, value: Part obj
                for c in fmt:        # a char of format 'Y'
                    ut = Char2UType[c]
                    # fill ut_parts
                    if ut in self.date_p:
                        my_od[ut] = self.date_p[ut]
                    else:
                        my_od[ut] = None
                fmt2myOD[fmt] = my_od
            return fmt2myOD

        def remove_unmatched_format(fmt2myOD):
            rm_fmt = []
            for fmt, my_od in fmt2myOD.items():
                part_objs = list(my_od.values())
                part_objs = list(filter(None, part_objs))
                if not strictly_increasing(part_objs):
                    rm_fmt.append(fmt)
            for i in rm_fmt:
                fmt2myOD.pop(i)

        def get_OK_fmts(fmt2myOD):
            """Find unused parts can push location.

            if any push range of unused part can't found, remove the format
            from fmt2myOD.

            OK_fmts:
            -------
            {fmt1: {lr:part_lr, lr:part_lr}, format1
             fmt2: {lr:part_lr, lr:part_lr}, format2
             fmt3: {lr:part_lr, lr:part_lr}} format3
            """
            rm_fmt = []
            OK_fmts = {}
            for fmt, my_od in fmt2myOD.items():
                skip = False    # append in rm_i
                ok_fills = {}
                for uup in self.unused_parts.subset['num']:
                    lr = find_range_can_push(my_od, uup)
                    if lr is None:
                        rm_fmt.append(fmt)
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
                fmt2myOD.pop(i)
            return OK_fmts

        def remove_lenlr_neq_Nplr(OK_fmts):
            # remove if len(lr) != num of part_lr, see fig2
            rm_fmt = []
            for fmt, d_lr2plr in OK_fmts.items():
                for lr, plrs in d_lr2plr.items():
                    dlr = lr[1]-lr[0]
                    n_plr = len(plrs)
                    if dlr != n_plr:
                        rm_fmt.append(fmt)
            for i in rm_fmt:
                OK_fmts.pop(i)

        def onlyone_format_fill(OK_fmts, date_p, fmt2myOD, nums):
            assert len(OK_fmts) == 1
            fmt = list(OK_fmts.keys())[0]
            fills_dict = list(OK_fmts.values())[0]
            mr_dict = mrange_dict(fills_dict)
            mr_dict.fill(self.date_p, fmt2myOD[fmt], nums)

        fmt2myOD = get_fmt2myOD(formats)
        remove_unmatched_format(fmt2myOD)  # remove in fmt2myOD
        OK_fmts = get_OK_fmts(fmt2myOD)
        remove_lenlr_neq_Nplr(OK_fmts)     # remove in OK_fmts
        if len(OK_fmts) == 1:
            nums = self.unused_parts.subset['num']
            onlyone_format_fill(OK_fmts, self.date_p, fmt2myOD, nums)
