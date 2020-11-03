import datetime
import re
from enum import Enum
import traceback

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

re_num = re.compile('\d+')
re_eng = re.compile('[a-zA-Z]+')
re_norm = re.compile('[-:,/ ]+')
re3 = [re_num, re_eng, re_norm]
sName = ['num', 'eng', 'norm', 'other']

nums = '0123456789'
engs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
norms= '-:.,/\ '

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
sType = Enum('sType', 'num eng norm other')

sType2exam = {sType.num:nums,   sType.eng:engs,   sType.norm:norms}
sType2re_c = {sType.num:re_num, sType.eng:re_eng, sType.norm:re_norm}
#type 0: number  [0-9]
#type 1: english [A-Za-z]
#type 2: chara   -:,/  <space>
#type 3: other
class uStat(Enum):
    unused    = 0
    simple    = 1 #re.finditer('\d+', '[a-zA-z]+'), add part_set
    lmrs      = 2 #lmrs time,  set_str_used
    bigpart   = 3

class uset(set):
    #TODO: add method remove, check
    #TODO: use dict
    def add(self, ele):
        if ele in self:
            raise KeyError('element {} already in set:\n{}'.format(ele, self))
        super().add(ele)

class Part():
    StrUsed = Enum('IsUsed', 'unused partused allused')
    def __init__(self, mstr, span:tuple,
                 stype=None, value=None):
        self.span = span
        self.mstr = mstr
        self.stype = self.check_stype(stype)
        self.value = self.get_value(value)
    
    def match_str(self):
        return self.mstr.in_str[self.span[0]:self.span[1]]
    
    def check_stype(self, stype):
        s = self.match_str()
        gstype = None
        for key in sType2exam:                         #detce first char
            if s[0] in sType2exam[key]:
                gstype = key
                break
        if len(s)>=2 and s[0] == '.' and s[1] in nums: #detct float number
            gstype = sType.num
        for c in s[1:]:                                #check others char
            if c not in sType2exam[gstype]:
                raise ValueError('check_stype faild {},\n{}'
                                 .format(gstype, self.mstr.mark(self.span)))
        assert gstype is not None
        if stype is not None and stype != gstype:
            raise ValueError('stype:{} != gstype:{}\n{}'
                             .format(stype, gstype, self.mstr.mark(self.span)))
        return gstype
    
    def get_value(self, v=None):
        s = self.match_str()
        value = None
        if self.stype == sType.num:
            if s[0] == '.':
                value = float(s)
            else:
                value = int(s)
        elif self.stype == sType.eng:
            S = s.upper()
            for key in ENG_STRS:
                ENG_STRS_Vi = ENG_STRS[key]
                if S in ENG_STRS_Vi:
                    v_index = ENG_STRS_Vi.index(S)
                    v_key = key
                    value = (v_key, v_index)
        else:
            value = v
        if v is not None:
            assert value == v
        return value
    
    def __str__(self):
        if isinstance(self.value, (int, float)):
            str_value = str(self.value)
        elif isinstance(self.value, tuple):
            s1=self.value[0][0].name
            s2=self.value[0][1].name if self.value[0][1] is not None else ''
            s3=self.value[1]
            str_value = '{}_{},{}'.format(s1, s2, s3)
        else:
            raise ValueError("self.value isn't int, float or tuple")
        ret = 'span={:>7}, str="{}", value={}'\
        .format(str(self.span), self.mstr.in_str[self.span[0]:self.span[1]],
                str_value)
        return ret
    
    def __eq__(self, other):
        return self.mstr == other.mstr and \
               self.span == other.span
    
    def __len__(self):
        return self.span[1] - self.span[0]
    
    def get_tuple(self):
        return tuple(self.span)
    
    def set_str_used(self):
        self.mstr.set_str_used(self.span)

#part date or time, can include sub part
class BigPart(dict):
    def __init__(self, mstr, mtype):
        '''
        @para inc: all sub parts increase, next part head after prev end.
        @para cont: all sub parts continuous, next part head close prev end.
        @para used: None not any, True is unused, False is allused
        
        dict's key: sType.norm or UType.xxx
        dict's value: Part object
        '''
        assert mtype in ABType
        super().__init__()
        self.mstr = mstr
        self.mtype= mtype
        self.span = [len(mstr.in_str),0]
        self.spilts = [] #each item is Part object
        
    def __setitem__(self, key, value):
        assert isinstance(value, Part)
        if key != sType.norm:
            #check key vaild for BigPartType
            d = {ABType.date:UxType['Date'], ABType.time:UxType['lmrTime']}
            if key not in d[self.mtype]:
                raise KeyError('key {} is invalid for BigPart {}'
                               .format(key, self.mtype))
            #check key is not using
            if key in self:
                raise KeyError('key {} is already in BigPart {} dict'
                               .format(key, self.mtype))
            super().__setitem__(key, value)
        else:
            self.spilts.append(value)
        #add set
        if hasattr(value, 'poped'):
            delattr(value, 'poped')  #Part obj poped
        else:
            self.mstr.part_set.add(value.get_tuple())
            value.set_str_used()
        #update self.span
        if value.span[0] < self.span[0]: #Part's left point over BigPart
            self.span[0] = value.span[0]
        if value.span[1] > self.span[1]: #Part's right point over BigPart
            self.span[1] = value.span[1]
    
    def pop(self, key):
        value = super().pop(key)
        value.poped = True
        return value
    
    def check_spans(self, inc=True, cont=False):
        last = self[0]
        start = last.span[0]
        for i in self[1:]:
            if inc and last.span[1] > i.span[0]:
                raise ValueError('sub part not increase')
            if cont and last.span[1] != i.span[0]:
                raise ValueError('sub part not continue')
            last = i
        end = last.span[1]
        return start, end

    def check_finally(self, req='MD hm'):
        #time not contain lmr
        d = {ABType.date:UxType['Date'], ABType.time:UxType['Time']}
        mset = d[self.mtype] #vaild UType by mstype
        req_char = set(req)          #set of chars in req
        char_vaild = req_char.intersection(Char2UType) #chars can found in dict
        req_UTypes = set(map(lambda x:Char2UType[x], char_vaild))
        want_check = req_UTypes.intersection(mset) #UTypes in mstype and req
        for ut in want_check:        #ut is a UType
            if ut not in self:
                return False
        return True
    
    def check_breakpoint(self):
        #TODO: raise show last+1
        '''
        check is middle broken, 
        such as found HH::SS without minute, YYYY//DD without month
        return True is not broken, False have probem
        '''
        keys = list(self.keys())
        key_v = list(map(lambda x:x.value, keys))
        key_v.sort()
        if len(key_v) >= 2:
            last = key_v[0]
            for i in key_v[1:]:
                if i != last+1:
                    key_n = list(map(lambda x:x.name, keys))
                    raise ValueError('found keys:{}, but not {}'
                                     .format(key_n, last+1))
                last = i
    
    def check_unused_char(self):
        '''
        check chars in self.span but not flag in self.mstr.used[i]
        raise error if invaild spilt or multipy continuous char
        '''
        allow_dict    = {ABType.date:'-./ ', ABType.time:' '}
        disallow_dict = {ABType.date:'O',    ABType.time:'O'}
        allow    = allow_dict[self.mtype]
        disallow = disallow_dict[self.mtype]
        self.mstr.check_unused_char(allow, disallow, self.span)
    
    def __str__(self):
        if len(self) != 0:
            ret = 'BigPart:---------------------------\n'
            for i in self:
                ret += '{:<12}:{}\n'.format(i, self[i])
            ret = ret[:-1]
            return ret
        else:
            return 'empty------------------------------'
        

class UnusedParts(list):
    def __init__(self, mstr):
        super().__init__()
        self.mstr = mstr
    
    def append(self, part):
        assert isinstance(part, Part)
        p_tuple = part.get_tuple()
        self.mstr.unused_part_set.add(p_tuple)
        super().append(part)
    
    def __getitem_delable(self, s):
        def delete():
            if v.deleted == True:
                raise RuntimeError('UnusedParts item already delete')
            self.delete(v.s)
            v.deleted = True
        
        v = super().__getitem__(s)
        v.deleted = False
        v.s = s
        v.delete = delete
        return v
    
    def onlyone_unused(self):
        if len(self) == 1:
            return self.__getitem_delable(0)
        else:
            return None
    
    def __str__(self):
        ret = 'UnusedParts:\n'
        for i in self:
            ret += str(i)
        return ret
    
    def delete(self, index):
        '''
        delete for Part obj in UnusedParts to BigPart,
        part can spilt some parts
        '''
        p = self.pop(index)
        p_tuple = p.get_tuple()
        self.mstr.unused_part_set.remove(p_tuple)

class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        #only modify in BigPart.__setitem__ through set_str_used
        self.used = [False]*len(in_str)
        self.disallow_unused_chars = ''

    def get_atype(self, re_comp, stype,
                  filter_used=Part.StrUsed.unused):
        """
        find all use re, atype of sub
        @para re_comp: re.compile object
        @para stype: type_id for Part object
        @para filter_used: only output unused
        """
        founds = re_comp.finditer(self.in_str)
        bpart = UnusedParts(self)
        for i in founds:
            str_used = self.is_str_used(i.span())
            if filter_used is None or str_used == filter_used:
                part = Part(self, i.span(), stype)
                bpart.append(part)
        return bpart
    
    def get_allsType_parts(self, sType2X_dict, names):
        ret = {}
        for key,n_i in zip(sType2X_dict, names):
            stype_i = key
            re_i = sType2X_dict[key]
            ret[n_i] = self.get_atype(re_i, stype_i)
        return ret
        
    def mark(self, index, num=1):
        if isinstance(index, tuple) and len(index) == 2:
            num = index[1] - index[0]
            index = index[0]
        elif isinstance(index, int):
            pass
        else:
            raise ValueError('index must len=2 or int')
        return "{}\n{}".format(self.in_str, ' '*index+'^'*num)
    
    def find_onlyone(self, sub):
        """
        find only one sub str or not contain.
        @para sub: the sub str
        @return: found index, -1 if not contain
        """
        index = self.in_str.find(sub)
        if index != -1:         #found
           more = self.in_str.find(sub, index+len(sub))
           if more != -1:       #found more
               raise ValueError('found multipy {} in str'.format(sub))
        return index
    
    def find_strs(self, subs, err):
        """
        find which sub in in_str, only one sub can find, else raise ValueError
        @para subs: list of subs
        @para err: show when find multipy subs
        @ret sub_i: the index of sub, when found the Part
        @ret ret_Part: found Part
        """
        ret = None
        for ni,sub in enumerate(subs):
            index = self.find_onlyone(sub)
            if index != -1:
                span = (index, index+len(sub))
                if ret is None:
                    ret = Part(self, span, sType.eng)
                else:
                    raise ValueError('found multipy {} in str'.format(err))
        return ret
    
    def search(self, pattern, start=0, end=None, isRaise=True, isCheck=True):
        found = re.search(pattern, self.in_str[start:end])
        if found is None:
            if isRaise:
                raise ValueError('search re pattern"{}" not found'
                                 .format(pattern))
            else:
                return None
        fsta = start+found.start(1)
        fend = start+found.end(1)
        if isCheck and pattern[0] != '^':
            self.check_spilt(fsta-1)
        if isCheck and pattern[-1]!= '$':
            self.check_spilt(fend)
        return found
    
    def check_spilt(self, index, allow=[' ', '|', '.'], isRaise=True):
        if 0<=index<len(self.in_str):
            char = self.in_str[index]
            if char not in allow and isRaise:
                raise ValueError("'{}' not in avabile spilt character{}\n{}"\
                .format(char, allow, self.mark(index)))
            return char
            return None
    
    def is_str_used(self, span):
        N_used = 0
        for i in range(*span):
            if self.used[i]:
                N_used += 1
        if N_used == 0:
            str_used = Part.StrUsed.unused
        elif N_used == span[1] - span[0]:
            str_used = Part.StrUsed.allused
        else:
            str_used = Part.StrUsed.partused
        return str_used
    
    #only can call in BigPart.__setitem__, pack by Part.set_str_used,
    #and check_unused_char
    def set_str_used(self, span):
        str_used = self.is_str_used(span)
        if str_used != Part.StrUsed.unused:
            raise ValueError('want the part of str unused, but str is {},\
not all unused\n{}'.format(str_used.name, self.mark(span)))
        for i in range(*span):
            self.used[i] = True
    
    def check_unused_char(self, allow, disallow, search_span):
        '''
        if char'O' in allow or disallow, as the defalut other,
        don't add other char if 'O' in str, is invaild
        char not in both allow and disallow, add to disallow for later call.
        '''
        if search_span is None:
            search_span = (0, len(self.in_str))
        allow = set(allow)
        disallow = set(disallow)
        assert set.isdisjoint(allow, disallow)
        other_allow    = 'O' in allow
        other_disallow = 'O' in disallow
        if other_allow:   #clear if 'O' in regular str
            allow = set()
        if other_disallow:
            disallow = set()
        #get unused_span_list: used flag of char is False spans
        unused_span_list = []
        last_span = [0,0]
        last_use = self.used[0]
        for i in range(search_span[0]+1, search_span[1]):
            use_i = self.used[i]
            if last_use and not use_i:  #last True, curr False
                last_span[0] = i
            if not last_use and use_i:  #last False, curr True
                last_span[1] = i
                unused_span_list.append(tuple(last_span))
            last_use = use_i
        #check and set_str_used
        for span in unused_span_list:
            if span[1] - span[0] != 1:
                raise ValueError('multiply unused char continuous\n{}'
                                 .format(self.mstr.mark(span)))
            else:
                i = span[0]
                assert span[1] == i+1
                c = self.in_str[i]
                if c in allow:
                    self.set_str_used(span)
                elif c in disallow:
                    raise ValueError('in call disallow unused char\n{}'
                                 .format(self.mark(i)))
                elif other_allow:
                    self.set_str_used(span)
                elif other_disallow:
                    raise ValueError('in call other char is disallow\n{}'
                                 .format(self.mark(i)))
                elif c in self.disallow_unused_chars:
                    raise ValueError('in My_str disallow unused char\n{}'
                                 .format(self.mark(i)))
                else:
                    #disable for later call
                    self.disallow_unused_chars += c
    
    def print_str_use_status(self):
        marks = ''
        for used_i in self.used:
            marks += {False:' ', True:'^'}[used_i]
        print('str use status\n{}\n{}'.format(self.in_str, marks))
    
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
    def __init__(self, in_str, find_date42=True, default_n2v='hours'):
        super().__init__(in_str)
        self.flags = [] #'time_found'
        self.para = {'fd42':find_date42, 'dn2v':default_n2v}
        self.part_set = uset()        #only for two BigPart
        self.unused_part_set = uset() #only for all UnusedParts obj
        self.date_p = BigPart(self, ABType.date)
        self.time_p = BigPart(self, ABType.time)
        self.process()
        self.check()
        
    def process(self):
        self.time_lmrs()
        self.english_month_weekday()
        self.parts = self.get_allsType_parts(sType2re_c, sName)
        self.find_date(self.num8)         #find YYYYMMDD
        if 'time_found' in self.flags or self.para['fd42']:
            self.find_date(self.num4)     #find YYYY, MMDD
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
        self.date_p.check_unused_char()
        self.time_p.check_unused_char()
        self.check_unused_char(allow=' ', disallow=':-./', search_span=None)
        
    def english_month_weekday(self):
        month = self.find_strs(month_short, 'english month')
        weekday = self.find_strs(weekday_short, 'english weekday')
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
            self.date_p[UType.day  ] = Part(self, (s+6, e),   sType.num)
            return True
        return False
    
    def num4(self, part):
        s = part.span[0]
        e = part.span[1]
        match = part.match_str()
        inti = int(match)
        if len(match) == 4:
            if 1970<=inti<2050:
                self.date_p[UType.year ] = Part(self, (s, e), sType.num)
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
        m = self.search('((\d+):(\d+:)*(\d+)(\.\d+)*)', isRaise=False)
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
            if key in self.time_p.keys():
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
        oouu = self.parts['num'].onlyone_unused()
        if oouu is not None:
            #TODO: use pop inserted delete, not remove in part_set
            oouu.delete()    #delete in UnusedParts and part_set
            self.date_p[UType.day] = oouu
    
    def check_bigparts_not_overlapped(self):
        if len(self.date_p)>=1 and len(self.time_p)>=1:
            date_time = self.date_p.span[1] <= self.time_p.span[0]
            time_date = self.time_p.span[1] <= self.date_p.span[0]
            assert date_time or time_date
    
    def as_datetime(self):
        U = UType
        dx = {U.Y:0, U.M:1, U.D:2, U.h:3, U.m:4, U.s:5}
        l = [None]*7    #temp for datetime paras  YMD,hms,us
        
        today = datetime.date.today()
        today = [today.year, today.month, today.day]
        d = {}
        for k in self.date_p.keys():
            d[k] = self.date_p[k]
        for k in self.time_p.keys():
            d[k] = self.time_p[k]
        for k in d:
            if k in dx:
                v = d[k].value
                if isinstance(v, tuple): #v is english month
                    v = v[1] + 1
                l[dx[k]] = v
        #subsec*1000000 to microsec int
        if U.subsec in d:
            l[6] = int(d[U.ss].value*1e6)
        #check start of item 3, and fill now paras
        i1 = 0
        while l[i1] is None and i1 < 3:
            l[i1] = today[i1]
            i1 += 1
        #check vaild item
        i2 = i1
        while l[i2] is not None and i2 < 6:
            i2 += 1
        if i2 - i1 < 2:
            raise ValueError('vaild item less than 2')
        #pop last items
        while len(l) > i2:
            l.pop()
        if U.ampm in d:
            if d[U.ampm].value[1] == 1:
                l[3] += 12
        #print(l)
        dt_obj = datetime.datetime(*l)
        if U.weekday in d and d[U.WD].value != dt_obj.weekday():
            raise ValueError('weekday in str is {}, but infer by date is {}'
                             .format(d[U.WD].match_str(), 
                            dt_obj.strftime('%Y-%m-%d %A')))
        return dt_obj

def test_a_list_str(test_list, expect_err=False, print_traceback=True):
    for i in test_list:
        print('str:', i)
        try:
            tstr = Time_str(i)
            dt = tstr.as_datetime()
            tstr.print_str_use_status()
            print('date:', tstr.date_p)
            print('time:', tstr.time_p)
        except Exception as e:
            if print_traceback:
                traceback.print_exc()
            else:
                print('error happend:')
                print(e)
            err_happend = True
        else:
            print('no error')
            err_happend = False
            print(dt)
        finally:
            if err_happend != expect_err:
                print('error not expect, expect is {}, but result is {}'
                      .format(expect_err, err_happend))
        print()
#test codes
if __name__ == '__main__':
    test_ok = ['Wed 28/Oct 12:34:56.123',
               '20201030','1030','10:30','30 10:30','10:22 PM']
    test_err = ['12:34:56:12', '12.34:34', 'Oct:12', '2020:12', '12 20:12 Oct']
    print('##########test_ok, should no error!!!!!!!!!!')
    test_a_list_str(test_ok, expect_err=False)
    print('##########test_err, should happend error each item!!!!!!!!!!')
    test_a_list_str(test_err, expect_err=True)
