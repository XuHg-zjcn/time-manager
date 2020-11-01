import datetime
import re
from enum import Enum

day_full=['Monday','Tuesday','Wednesday','Thursday',
          'Friday','Saturday','Sunday']
day_short=['Mon','Tue','Wed','Thur','Fri','Sat','Sun']
month_full=['January','February','March','April','May','June',
            'July','August','Spetember','October','November','December']
month_short=['Jan','Feb','Mar','Apr','May','Jun',
             'Jul','Aug','Spet','Oct','Nov','Dec']
ampm = ['AM', 'PM']

eType = Enum('eType', 'day month ampm')
fType = Enum('fType', 'full short')
eng_strs = {(eType.day, fType.full):day_full,
            (eType.day, fType.short):day_short,
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
AType = Enum('AType', 'year month date day')
class BType(Enum):
    ampm = 0
    hours = 1
    minute = 2
    second = 3
    subsec = 4
    ap = 0
    H = 1
    M = 2
    S = 3
    SS = 4
    left = 5
    midd = 6
    right = 7
    l = 5
    m = 6
    r = 7
sType = Enum('sType', 'num eng norm other')

sType2exam = {sType.num:nums,   sType.eng:engs,   sType.norm:norms}
sType2re_c = {sType.num:re_num, sType.eng:re_eng, sType.norm:re_norm}
#type 0: number  [0-9]
#type 1: english [A-Za-z]
#type 2: chara   -:,/  <space>
#type 3: other

class Part():
    StrUsed = Enum('IsUsed', 'unused partused allused')
    objs = []
    def __init__(self, mstr, span:tuple, stype=None, value=None, isUse=True):
        self.span = span
        self.mstr = mstr
        self.stype = self.check_stype(stype)
        self.value = self.get_value(value)
        self.str_used = self.is_str_used()
        self.isUse = False
        if isUse:
            self.check_no_repeat()
            self.set_used()
    
    def match_str(self):
        return self.mstr.in_str[self.span[0]:self.span[1]]
    
    def check_stype(self, stype):
        s = self.match_str()
        gstype = None
        for key in sType2exam:
            if s[0] in sType2exam[key]:
                gstype = key
                break
        if len(s)>=2 and s[0] == '.' and s[1] in nums: #detct float number
            gstype = sType.num
        for c in s[1:]:
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
        ret = 'span={:>7}, str="{}", str_used={}, isUse={}, value={}'\
        .format(str(self.span), self.mstr.in_str[self.span[0]:self.span[1]],
                self.str_used.name, self.isUse, str_value)
        return ret
    
    def __lt__(self, other):
        return self.span[1] < other.span[0]
    
    def __gt__(self, other):
        return self.span[1] > other.span[0]
    
    def __eq__(self, other):
        return self.mstr == other.mstr and \
               self.span == other.span
    
    def check_no_repeat(self):
        for i in Part.objs:
            if i == self:
                raise ValueError('Part {} is already create\n{}'
                .format(self.span, self.mstr.mark(self.span)))
    
    def is_str_used(self):
        N_used = 0
        for i in range(*self.span):
            if self.mstr.used[i]:
                N_used += 1
        if N_used == 0:
            str_used = Part.StrUsed.unused
        elif N_used == self.span[1] - self.span[0]:
            str_used = Part.StrUsed.allused
        else:
            str_used = Part.StrUsed.partused
        return str_used
    
    def set_used(self):
        self.str_used = self.is_str_used()
        if self.str_used != Part.StrUsed.unused:
            raise ValueError('want the part of str unused, but str is {},\
not all unused\n{}'.format(self.str_used, self.mstr.mark(self.span)))
        self.objs.append(self)
        for i in range(*self.span):
            self.mstr.used[i] = True
        self.str_used = Part.StrUsed.allused
        self.isUse = True
    
    def __len__(self):
        return self.span[1] - self.span[0]

#part date or time, can include sub part
class BigPart(dict):
    def __init__(self, mtype, inc=False, cont=False, used=None):
        '''
        @para inc: all sub parts increase, next part head after prev end.
        @para cont: all sub parts continuous, next part head close prev end.
        @para used: None not any, True is unused, False is allused
        '''
        assert mtype in ABType
        super().__init__()
        self.mtype = mtype
        self.inc = inc
        self.cont = cont
        self.used = used
        self.x_len = 0
        self.aslist = []
        
    def __setitem__(self, key, value):
        assert isinstance(value, Part)
        if key != sType.norm:
            if self.mtype == ABType.date:
                assert key in AType
            if self.mtype == ABType.time:
                assert key in BType
            if key in self:
                raise KeyError('key {} is already in BigPart {} dict'
                               .format(key, self.mtype))
            super().__setitem__(key, value)
        if value not in self.aslist:  #no repeating Parts in self.aslist
            self.aslist.append(value)
        self.x_len += 1
        if self.used is not None and self.used != value.isUse:
            raise ValueError('used reqire is not same')
        if self.x_len >= 2:
            if self.inc and self.aslist[-2] > self.aslist[-1]:
                raise ValueError('sub part not increase:\n{}'.format(self))
            if self.cont and self.aslist[-2] != self.aslist[-1]:
                raise ValueError('sub part not continue:\n{}'.format(self))
    
    def __getitem__(self, key):
        if key in self:
            value = super().__getitem__(key)
        elif isinstance(key, int):
            if key>=0:
                value = self.aslist[self.x_len+key]
            elif key<0:
                value = self.aslist[key]
            else:
                raise KeyError("{} isn't valid key or index".format(key))
        else:
            raise KeyError("{} isn't valid key or index".format(key))
        return value
    
    def check_used(self):
        for i in self:
            self[i].check_used()
    
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
        self.span = (start, end)

    def check_finally(self, req='MD hm'):
        d1 = {'Y':AType.year, 'M':AType.month, 'D':AType.date}
        d2 = {'h':BType.hours, 'm':BType.minute, 's':BType.second}
        dx = {ABType.date:d1, ABType.time:d2}[self.mtype]
        for key in dx:
            if key in req and dx[key] not in self:
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
    
    def __str__(self):
        ret = 'BigPart:\n'
        for i in self:
            ret += '{:<12}:{}\n'.format(i, self[i])
        return ret

class UnusedParts(list):
    def __init__(self):
        super().__init__()
        
    def append(self, obj):
        assert isinstance(obj, Part)
        super().append(obj)
    
    def unuseds(self):
        n = []
        for i in self:
            if i.is_str_used() == Part.StrUsed.unused:
                n.append(i)
        return n
    
    def onlyone_unused(self):
        unused_list = self.unuseds()
        if len(unused_list) == 1:
            return unused_list[0]
        else:
            return None

class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        self.used = [False]*len(in_str)

    def get_atype(self, re_comp, stype,
                  filter_used=Part.StrUsed.unused):
        """
        find all use re, atype of sub
        @para re_comp: re.compile object
        @para stype: type_id for Part object
        @para filter_used: only output unused
        """
        founds = re_comp.finditer(self.in_str)
        bpart = UnusedParts()
        for i in founds:
            part = Part(self, i.span(), stype, isUse=False)
            if filter_used is None or part.str_used == filter_used:
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
    
#smart time str to datetime struct
class Time_str(My_str):
    '''
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
    check_result
    as datetime object
    
    part add rule:
        BigPart no breakpoint,           exam: YYYY//DD without month
        limted use spilt char,           ':' for time, '-.,/\ ' for date
        Parts no overlapped on str,      each char of in_str has flag
        two BigPart not overlapped,      exam: YYYY/MM hh:DD:mm:ss
        a Part can only add to a BigPart
    '''
    def __init__(self, in_str, find_date42=True, default_n2v='hours'):
        super().__init__(in_str)
        self.flags = [] #'time_found'
        self.para = {'fd42':find_date42, 'dn2v':default_n2v}
        self.date_p = BigPart(ABType.date)
        self.time_p = BigPart(ABType.time, used=None)
        self.process()
        self.check()
        
    def process(self):
        self.time_lmrs()
        self.english_month_day()
        self.parts = self.get_allsType_parts(sType2re_c, sName)
        self.date_num8()         #find YYYYMMDD
        if 'time_found' in self.flags or self.para['fd42']:
            self.date_num4()     #find YYYY, MMDD
            self.onlyone_unused_num_as_date()
        if len(self.date_p) > 0:
            self.set_time_p('hours')  #date found
        else:
            self.set_time_p(self.para['dn2v'])
    
    def check(self):
        self.date_p.check_breakpoint()
        
    def english_month_day(self):
        month = self.find_strs(month_short, 'english month')
        day = self.find_strs(day_short, 'english day')
        apm = self.find_strs(ampm, 'AMPM')
        if month is not None:
            self.date_p[AType.month] = month
        if day is not None:
            self.date_p[AType.day] = day
        if apm is not None:
            self.time_p[BType.ampm] = apm
    
    def date_num8(self):
        for part in self.parts['num']:
            s = part.span[0]
            e = part.span[1]
            match = part.match_str()
            if len(match) == 8:
                self.date_p[AType.year] = Part(self, (s,   s+4), sType.num)
                self.date_p[AType.month]= Part(self, (s+4, s+6), sType.num)
                self.date_p[AType.date] = Part(self, (s+6, e),   sType.num)
                part.str_used = Part.StrUsed.allused
    
    def date_num4(self):
        for part in self.parts['num']:
            s = part.span[0]
            e = part.span[1]
            match = part.match_str()
            inti = int(match)
            if len(match) == 4:
                if 1970<=inti<2050:
                    self.date_p[AType.year] = Part(self, (s, e), sType.num)
                    part.str_used = Part.StrUsed.allused
                elif 101<=inti<=1231:
                    self.date_p[AType.month]= Part(self, (s, s+2), sType.num)
                    self.date_p[AType.date] = Part(self, (s+2, e), sType.num)
                    part.str_used = Part.StrUsed.allused
         
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
        self.time_p[BType.left] = Part(self, m.span(2), sType.num)
        self.time_p[sType.norm] = Part(self, (m.end(2), m.end(2)+1), sType.norm)
        if m.group(3) is not None:
            self.time_p[BType.midd] = Part(self, (m.start(3),m.end(3)-1), sType.num)
            self.time_p[sType.norm] = Part(self, (m.end(3)-1, m.end(3)), sType.norm)
        self.time_p[BType.right] = Part(self, m.span(4), sType.num)
        if m.group(5) is not None:
            self.time_p[BType.subsec] = Part(self, m.span(5), sType.num)
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
        B = BType
        #            src_keys              dst_keys
        dict_rule = {(B.l, B.m, B.r)      :(B.H, B.M, B.S      ),
                     (B.l, B.m, B.r, B.SS):(B.H, B.M, B.S, None),
                     (          B.r, B.SS):(          B.S, None),
                     (B.l,      B.r, B.SS):(     B.M, B.S, None)}
        #get src_keys
        src_keys = []
        for key in (B.l, B.m, B.r, B.SS):
            if key in self.time_p:
                src_keys.append(key)
        src_keys = tuple(src_keys)
        #use dict_rule
        if src_keys in dict_rule:
            dst_keys = dict_rule[src_keys]
        #use n2v
        elif src_keys == (B.l, B.r):
            if n2v == 'hours':
                dst_keys = (B.H, B.M)
            elif n2v == 'second':
                dst_keys = (B.M, B.S)
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
            self.date_p[AType.date] = oouu
            oouu.set_used()
         
if __name__ == '__main__':
    test_strs = ['Wed 28/Oct 12:34:56.123',
                 '20201030',
                 '1030',
                 '10:30',
                 '31 10:30',
                 '20:22 PM']
    for i in test_strs:
        print(i)
        tstr = Time_str(i)
        print('date:', tstr.date_p)
        print('time:', tstr.time_p)
        print()
