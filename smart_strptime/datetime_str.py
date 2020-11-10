import datetime                                    # L0 built-in model
from my_lib import strictly_increasing             # L1 my_lib
from my_lib import my_odict, mrange_dict
from my_lib import part_lr
from basetime import UType, Char2UType             # L3 basetime define
from lmrTime_str import lmrTime_str                # L4 time search type
from Date_str import Date_str
# level of the module is L5, can use outside package


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

    def __init__(self, in_str, fd642=True, default_n2v='hour', YY2=True):
        super().__init__(in_str)
        # self.flags 'time_found', 'fd642', 'YY2', 'process OK'
        self.para = {'dn2v': default_n2v}  # default time format
        if fd642:
            self.flags.add('fd642')  # find 6,4,2 digts without time found
        if YY2:
            self.flags.add('YY2')    # allow 19YY or 20YY

    def process_check(self):
        """Call after init."""
        assert 'process OK' not in self.flags  # not entry before
        self.process()
        self.check()
        self.flags.add('process OK')

    def process(self):
        """Process input str."""
        lmrTime_str.process(self)
        Date_str.process(self)
        if len(self.date_p) > 0:  # any about date found
            self.set_time_p('hour')
        else:
            self.set_time_p(self.para['dn2v'])

    def check(self):
        """Check process result."""
        date_skips = {UType.Nweek.value, UType.weekday.value}
        self.date_p.check_breakpoint(date_skips)
        self.time_p.check_breakpoint()
        # TODO: check time_p
        self.check_bigparts_not_overlapped()
        self.date_p.check_unused_char('-./ ', 'O')
        self.time_p.check_unused_char(' ', 'O')
        self.check_unused_char(' ', ':-./')
        assert len(self.unused_parts) == 0
        assert all(self.used)

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
            mr_dict.fill(self.date_p, fmt2myOD[fmt])

        fmt2myOD = get_fmt2myOD(formats)
        remove_unmatched_format(fmt2myOD)  # remove in fmt2myOD
        OK_fmts = get_OK_fmts(fmt2myOD)
        remove_lenlr_neq_Nplr(OK_fmts)     # remove in OK_fmts
        if len(OK_fmts) == 1:
            nums = self.unused_parts.subset['num']
            onlyone_format_fill(OK_fmts, self.date_p, fmt2myOD, nums)
