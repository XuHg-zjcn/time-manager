#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re
from enum import Enum
import traceback
import time
from my_str import Part, BigPart, My_str
from my_str import sType, sType2re_c, sName
from my_lib import strictly_increasing, my_odict, uset
from my_lib import mrange_dict, part_lr
import functools

weekday_full=['Monday','Tuesday','Wednesday','Thursday',
          'Friday','Saturday','Sunday']
weekday_short=['Mon','Tue','Wed','Thur','Fri','Sat','Sun']
month_full=['January','February','March','April','May','June',
            'July','August','Spetember','October','November','December']
month_short=['Jan','Feb','Mar','Apr','May','Jun',
             'Jul','Aug','Spet','Oct','Nov','Dec']
ampm = ['AM', 'PM']

eType = Enum('eType', 'weekday month ampm')
fType = Enum('fType', 'full short')
eng_strs = {(eType.weekday, fType.full):weekday_full,
            (eType.weekday, fType.short):weekday_short,
            (eType.month, fType.full):month_full,
            (eType.month, fType.short):month_short,
            (eType.ampm, None):ampm}
def upper_d(k):
    v = eng_strs[k]
    return k, list(map(lambda x:(x.upper()), v))
ENG_STRS = dict(map(upper_d, eng_strs))

re_lmrs = re.compile('((\d+):(\d+:)?(\d+)(\.\d+)?)')

ABType = Enum('ABType', 'date time')
class UType(Enum):
    #date
    year = 0
    month = 1
    day = 2
    weekday = 3  #can skip in check_breakpoint
    Y = 0
    M = 1
    D = 2
    WD = 3
    #time
    ampm = 4  #can skip in check_breakpoint
    hours = 5
    minute = 6
    second = 7
    subsec = 8
    ap = 4
    h = 5
    m = 6
    s = 7
    ss = 8
    #time lmr
    left = 9
    midd = 10
    right = 11
    lt = 9
    md = 10
    rt = 11
def dt(U):
    Date = {U.Y, U.M, U.D, U.WD}
    Time = {U.ap, U.h, U.m, U.s, U.ss}
    lmr  = {U.lt, U.md, U.rt}
    lmrT = set.union(Time, lmr)
    UxType = {'Date':Date, 'Time':Time, 'lmr':lmr, 'lmrTime':lmrT}
    Char2UType = {'Y':U.Y, 'M':U.M, 'D':U.D, 'W':U.WD,
                  'p':U.ap, 'h':U.h, 'm':U.m, 's':U.s, 'S':U.ss}
    return UxType, Char2UType
UxType, Char2UType = dt(UType)
#UType2Char = {v:k for k,v in Char2UType.items()}

#smart time str to datetime struct
class Time_str(My_str):
    '''
    pseudo-code:
    find ll:mm:rr.ss, english
    TODO: extend word
    find YYYYMMDD
    if time_found or flags.find_date42:
        find YYYY, MMDD
        find DD, if onlyone num
    if any about date found:
        set_time_p(n2v='hours')
    else:
        set_time_p(n2v=default_n2v)
  TODO: check_result
  TODO: as datetime object
    
    part add rule:
        BigPart no breakpoint,           exam: YYYY//DD without month
        limted use spilt char,           time':', date'-./\ ' BigPart',T'
        Parts no overlapped on str,      each char of in_str has flag
        two BigPart not overlapped,      exam: YYYY/MM hh:mm:ss DD
        a Part can only add to a BigPart
        Parts in BigPart are not repeating
    '''
    def __init__(self, in_str, fd642=True, default_n2v='hours', YY2=False):
        super().__init__(in_str)
        self.flags = [] #'time_found'
        self.para = {'dn2v':default_n2v}
        if fd642: self.flags.append('fd642')
        if YY2:   self.flags.append('YY2')
    
    def process_check(self):
        assert 'process OK' not in self.flags
        self.part_set = uset()        #only for two BigPart
        self.unused_part_set = uset() #only for all UnusedParts obj
        self.date_p = BigPart(self, 'date', UxType['Date'])
        self.time_p = BigPart(self, 'time', UxType['lmrTime'])
        self.process()
        self.check()
        self.flags.append('process OK')
        
    def process(self):
        self.time_lmrs()
        self.english_month_weekday()
        self.parts = self.get_allsType_parts(sType2re_c, sName)
        self.find_date(self.num8)         #find YYYYMMDD
        if ('time_found' in self.flags) or ('fd642' in self.flags):
            self.find_date(self.num4)     #find YYYY, MMDD
            self.find_date(self.num6)     #find YYYYMM
            self.unused_chooise()
            self.onlyone_unused_num_as_date()
        if len(self.date_p) > 0:
            self.set_time_p('hours')  #date found
        else:
            self.set_time_p(self.para['dn2v'])
        del self.parts
    
    def check(self):
        self.date_p.check_breakpoint()
        #TODO: check time_p
        self.check_bigparts_not_overlapped()
        self.date_p.check_unused_char('-./ ', 'O')
        self.time_p.check_unused_char(' ', 'O')
        self.check_unused_char(' ', ':-./')
        
    def english_month_weekday(self):
        month = self.find_strs(month_short, puls1=True)
        weekday = self.find_strs(weekday_short, puls1=False)
        apm = self.find_strs(ampm, 'AMPM')
        if month is not None:
            self.date_p[UType.month] = month
        if weekday is not None:
            self.date_p[UType.weekday] = weekday
        if apm is not None:
            self.time_p[UType.ampm] = apm
    
    def find_date(self, func):
        pop_i = None
        for ni,part in enumerate(self.parts['num']):
            if func(part) == True:
                if pop_i is None:
                    pop_i = ni
                    self.parts['num'].delete(ni)
    
    def num8(self, part):
        s = part.span[0]
        e = part.span[1]
        match = part.match_str()
        if len(match) == 8:
            self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
            self.date_p[UType.month] = Part(self, (s+4, s+6), sType.num)
            self.date_p[UType.day  ] = Part(self, (s+6, e  ),   sType.num)
            return True
        return False
    
    def num6(self, part):
        def YYYYMM(self, s, e):
            self.date_p[UType.year ] = Part(self, (s,   s+4), sType.num)
            self.date_p[UType.month] = Part(self, (s+4, e  ),   sType.num)
        def YYMMDD(self, s, e):
            self.date_p[UType.year ] = Part(self, (s,   s+2), sType.num)
            self.date_p[UType.month] = Part(self, (s+2, s+4), sType.num)
            self.date_p[UType.month] = Part(self, (s+4, e  ), sType.num)
        s = part.span[0]
        e = part.span[1]
        match = part.match_str()
        if len(match) == 6:
            if 'YY2' in self.flags: 
                if 1913<=int(match[:4])<2100:
                    YYYYMM(self, s, e)
                else:
                    YYMMDD(self, s, e)
            else:
                YYYYMM(self, s, e)
            return True
        return False
    
    def num4(self, part):
        s = part.span[0]
        e = part.span[1]
        match = part.match_str()
        inti = int(match)
        if len(match) == 4:
            if 1970<=inti<2050:
                self.date_p[UType.year ] = Part(self, (s, e  ), sType.num)
                return True
            elif 101<=inti<=1231:
                self.date_p[UType.month] = Part(self, (s, s+2), sType.num)
                self.date_p[UType.day  ] = Part(self, (s+2, e), sType.num)
                return True
        return False
         
    def time_lmrs(self):
        """
        get time HH:MM:SS.subsec , MM:SS.subsec or HH:MM:SS
        return Left:Midd:Right.subsec
        if not found Midd or subsec, return None
        """
        m = self.search(re_lmrs, isRaise=False)
        if m is None:
            return None
        self.flags.append('time_found')
        #append Parts to self.time_parts
        self.time_p[UType.left] = Part(self, m.span(2),              sType.num)
        self.time_p[sType.norm] = Part(self, (m.end(2), m.end(2)+1), sType.norm)
        if m.group(3) is not None:
            self.time_p[UType.midd] = Part(self, (m.start(3),m.end(3)-1), sType.num)
            self.time_p[sType.norm] = Part(self, (m.end(3)-1, m.end(3)),  sType.norm)
        self.time_p[UType.right]    = Part(self, m.span(4), sType.num)
        if m.group(5) is not None:
            self.time_p[UType.subsec]=Part(self, m.span(5), sType.num)
        #get left, midd, right, subsec
    
    def set_time_p(self, n2v=None):
        '''
        ll:mm:rr        -> HH:MM:SS
        ll:mm:rr.sss... -> HH:MM:SS.subsec
              rr.sss... ->       SS.subsec
        ll :  rr.sss... ->    MM:SS.subsec
        ll :  rr          ?-> HH:MM or MM:SS
        @para n2v: if found ll:rr, such as 12:34,
                   'hours' for HH:MM, 'second' for MM:SS, None raise ValueError
        '''
        assert 'set_time_p' not in self.flags
        B = UType
        #            src_keys              dst_keys
        dict_rule = {(B.lt, B.md, B.rt)      :(B.h, B.m, B.s      ),
                     (B.lt, B.md, B.rt, B.ss):(B.h, B.m, B.s, None),
                     (            B.rt, B.ss):(          B.s, None),
                     (B.lt,       B.rt, B.ss):(     B.m, B.s, None)}
        #get src_keys
        src_keys = []
        for key in (B.lt, B.md, B.rt, B.ss):
            if key in self.time_p:
                src_keys.append(key)
        src_keys = tuple(src_keys)
        #use dict_rule
        if src_keys in dict_rule:
            dst_keys = dict_rule[src_keys]
        #use n2v
        elif src_keys == (B.lt, B.rt):
            if n2v == 'hours':
                dst_keys = (B.h, B.m)
            elif n2v == 'second':
                dst_keys = (B.m, B.s)
            else:
                raise ValueError('n2v must be hours or second')
        #no src_keys
        elif src_keys == ():
            return
        else:
            raise KeyError('src_keys {} not match'.format(src_keys))
        assert len(src_keys) == len(dst_keys)
        for s_k,d_k in zip(src_keys, dst_keys):
            if d_k is not None:
                self.time_p[d_k] = self.time_p.pop(s_k)
        self.flags.append('set_time_p')

    def onlyone_unused_num_as_date(self):
        oouu = self.parts['num'].pop_onlyone_unused()
        if oouu is not None:
            #TODO: use pop inserted delete, not remove in part_set
            self.date_p[UType.day] = oouu

    def check_bigparts_not_overlapped(self):
        if len(self.date_p)>=1 and len(self.time_p)>=1:
            date_time = self.date_p.span[1] <= self.time_p.span[0]
            time_date = self.time_p.span[1] <= self.date_p.span[0]
            if not (date_time or time_date):
                raise ValueError('date and time bigparts has overlapped\n\
str :{}\ndate:{}\ntime:{}'
.format(self.in_str,
        self.mark(self.date_p.span, out_str=False),
        self.mark(self.time_p.span, out_str=False)))
    
    def as_datetime(self):
        def get_nNone_and_fill(dt_paras, today):
            #get start of not None item in date, fill today paras, if None
            s = 0
            while dt_paras[s] is None and s < 3:
                dt_paras[s] = today[s]
                s += 1
            #get end of not None item
            e = s
            while dt_paras[e] is not None and e < 6:
                e += 1
            if e - s < 3:
                raise ValueError('vaild item less than 3:\n{}'
                                 .format(dt_paras))
            return s,e
        
        U = UType
        UT2num = {U.Y:0, U.M:1, U.D:2, U.h:3, U.m:4, U.s:5}
        dt_paras = [None]*7    #temp for datetime paras  YMD,hms,us
        
        today = datetime.date.today()
        today = [today.year, today.month, today.day]
        d = {}  #key:UType, value:Part obj
        for k in self.date_p.keys():
            d[k] = self.date_p[k]
        for k in self.time_p.keys():
            d[k] = self.time_p[k]
        #fill d(dict) into l(datetime para list), key in both d and dx
        dks = set.intersection(set(d.keys()), set(UT2num.keys()))
        for k in dks:
            dt_paras[UT2num[k]] = d[k].value
        #subsec*1000000 to microsec int
        if U.subsec in d:
            dt_paras[6] = int(d[U.ss].value*1e6)
        #get index range of value not None
        nNs,nNe = get_nNone_and_fill(dt_paras, today)
        #pop last None items
        while len(dt_paras) > nNe:
            dt_paras.pop()
        if U.ampm in d:
            if d[U.ampm].value == 1:
                dt_paras[3] += 12
        #print(dt_paras)
        dt_obj = datetime.datetime(*dt_paras)
        if U.weekday in d and d[U.WD].value != dt_obj.weekday():
            raise ValueError('weekday in str is {}, but infer by date is {}'
                             .format(d[U.WD].match_str(), 
                            dt_obj.strftime('%Y-%m-%d %A')))
        return dt_obj
    
    def unused_chooise(self, formats=['YMD', 'DMY', 'YM']):
        ''' D  M  Y-<      allows
            Y  M  D |
        n1 =|--|--|-^
        n2 ____|  |
        n3 _______|
        
        ^
        |
        date_p, bpart['num']
        '''
        def find_range_can_push(my_od, part_obj):
            lr = my_od.get_allow_lr(part_obj)
            if lr is None:
                return None
            else:
                li, ri = lr
                Left  = my_od.next_None(li, prev_next=1)    #[Left, Right)
                Right = my_od.next_None(ri, prev_next=-1)+1 #Right+1
                return Left, Right
        
        ut_fmts = {}             #key: format str, value: my_odict
        for fmt in formats:      #a format         'YMD'
            my_od = my_odict()
            for c in fmt:        #a char of format 'Y'
                ut = Char2UType[c]
                #fill ut_parts
                if ut in self.date_p:
                    my_od[ut] = self.date_p[ut]
                else:
                    my_od[ut] = None
            ut_fmts[fmt] = my_od
        #remove reverse format
        rm_fmt = []
        for fmt, my_od in ut_fmts.items():
            part_objs = list(my_od.values())
            part_objs = list(filter(None, part_objs))
            if not strictly_increasing(part_objs):
                rm_fmt.append(fmt)
        for i in rm_fmt: ut_fmts.pop(i)
        #find unused parts can push location
        rm_fmt = []
        OK_fmts = {}
        '''
        {{uup.tuple:(uup,lr), uup.tuple:(uup,lr)}, format1
         [uup.tuple:(uup,lr), uup.tuple:(uup,lr)], format2
         [uup.tuple:(uup,lr), uup.tuple:(uup,lr)]} format3
        '''
        for fmt,my_od in ut_fmts.items():
            skip = False    #append in rm_i
            ok_fills = {}
            for nj,uup in enumerate(self.parts['num']):
                lr = find_range_can_push(my_od, uup)
                if lr is None:
                    rm_fmt.append(fmt)
                    skip = True
                    break
                else:
                    if lr not in ok_fills:
                        ok_fills[lr] = []
                    ok_fills[lr].append(part_lr(fmt, uup, nj, lr))
            if skip:
                continue
            else:
                OK_fmts[fmt] = ok_fills
        for i in rm_fmt: ut_fmts.pop(i)
        
        #remove lr place != num of part_lr
        rm_fmt = []
        for fmt,d_lr2plr in OK_fmts.items():
            for lr,plrs in d_lr2plr.items():
                dlr = lr[1]-lr[0]
                n_plr = len(plrs)
                if dlr != n_plr:
                    rm_fmt.append(fmt)
        for i in rm_fmt: OK_fmts.pop(i)
        '''
         0   1  2  3  4
        left         right
        [//][ ][ ][ ][//]
            |---lr---|     lr=(1,4)
             ^  ^  ^
             |  |  |
             n1 n2 n3     n* are Part obj
        [n1,n2,n3].sort()
        '''
        if len(OK_fmts) == 1:
            #put part into good UType place
            fmt = list(OK_fmts.keys())[0]
            fills_dict = list(OK_fmts.values())[0]
            mr_dict = mrange_dict(fills_dict)
            mr_dict.fill(self.date_p, ut_fmts[fmt], self.parts['num'])

def test_a_list_str(test_list, expect_err=False, print_traceback=True):
    t_sum = 0
    for i in test_list:
        try:
            t0 = time.time()
            tstr = Time_str(i)
            tstr.process_check()
            #dt_obj = tstr.as_datetime()
        except Exception as e:
            t1 = time.time()
            tstr.print_str_use_status('v')
            if print_traceback:
                traceback.print_exc()
            else:
                print('error happend:')
                print(e)
            err_happend = True
        else:
            t1 = time.time()
            tstr.print_str_use_status('v')
            print('date:', tstr.date_p)
            print('time:', tstr.time_p)
            err_happend = False
            #print('datetime out:',dt_obj)
            print('no error')
        finally:
            t_sum += t1 - t0
            if err_happend != expect_err:
                print('error not expect, expect is {}, but result is {}'
                      .format(expect_err, err_happend))
            print('process {:.3f}ms'.format((t1-t0)*1000))
        print()
    return t_sum

#test codes
if __name__ == '__main__':
    import os
    test_ok = ['Wed 28/Oct 12:34:56.123',
               '20201030','1030','10:30 a','30 10:30','10:22 PM',
               '2020 10 5', '2020/11/5', '2020-11/5', '2020 Nov 5',
               '2020 5 Nov', '5 Nov 2020', '5/Nov/2020', '5 Nov. 2020',
               '202010','2020 10','2020 Nov', '2020Nov', '2020 Nov.']
    t_sum = 0
    test_err = ['12:34:56:12', '12.34:34', 'Oct:12', '2020:12', '12 20:12 Oct']
    os.system('clear')
    print('##########test_ok, should no error!!!!!!!!!!')
    t_sum += test_a_list_str(test_ok, expect_err=False, print_traceback=True)
    print('##########test_err, should happend error each item!!!!!!!!!!')
    #t_sum += test_a_list_str(test_err, expect_err=True, print_traceback=False)
    print('total use {:.3f}ms'.format(t_sum*1000))
