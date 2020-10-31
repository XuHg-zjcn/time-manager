import datetime
import re
from enum import Enum
from collections import Iterable

day_full=['Monday','Tuesday','Wednesday','Thursday',
          'Friday','Saturday','Sunday']
day_short=['Mon','Tue','Wed','Thur','Fri','Sat','Sun']
month_full=['January','February','March','April','May','June',
            'July','August','Spetember','October','November','December']
month_short=['Jan','Feb','Mar','Apr','May','Jun',
             'Jul','Aug','Spet','Oct','Nov','Dec']


re_num = re.compile('\d+')
re_eng = re.compile('[a-zA-Z]+')
re_norm = re.compile('[-:,/ ]+')
re3 = [re_num, re_eng, re_norm]
sName = ['num', 'eng', 'norm', 'other']

ABType = Enum('ABType', 'date time subs')
AType = Enum('AType', 'year month date day')
BType = Enum('BType', 'hours minute second subsec ampm left midd right')
sType = Enum('sType', 'num eng norm')
#type 0: number  [0-9]
#type 1: english [A-Za-z]
#type 2: chara   -:,/  <space>
#type 3: other

class Part():
    StrUsed = Enum('IsUsed', 'unused partused allused')
    objs = []
    def __init__(self, mstr, stype, span:tuple, isUse=True):
        self.span = span
        self.mstr = mstr
        self.stype = stype
        #TODO: self.stype_check()
        #TODO: add value
        self.check_str_used()
        if isUse:
            self.check_no_repeat()
            self.set_used()
        self.isUse = isUse
    
    def match(self):
        return self.mstr.in_str[self.span[0]:self.span[1]]
    
    def __str__(self):
        ret = 'span={} str="{}", str_used={}, isUse={}'\
        .format(self.span, self.mstr.in_str[self.span[0]:self.span[1]], 
                self.str_used, self.isUse)
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
    
    def check_str_used(self):
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
        self.str_used = str_used
    
    def set_used(self):
        self.check_str_used()
        if self.str_used != Part.StrUsed.unused:
            raise ValueError('want the part of str unused, but str is {},\
not all unused\n{}'.format(self.str_used, self.mstr.mark(self.span)))
        self.objs.append(self)
        for i in range(*self.span):
            self.mstr.used[i] = True
        self.str_used = Part.StrUsed.allused
    
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
            if self.mtype != ABType.subs and key in self:
                raise KeyError('key {} is already in BigPart {} dict'
                               .format(key, self.mtype))
            super().__setitem__(key, value)
        self.aslist.append(value)
        self.x_len += 1
        if self.used is not None and self.used != value.isUsed:
            raise ValueError('used reqire is not same')
        if self.x_len >= 2:
            if self.inc and self.aslist[-2] > self.aslist[-1]:
                raise ValueError('sub part not increase:\n{}'.format(self))
            if self.cont and self.aslist[-2] != self.aslist[-1]:
                raise ValueError('sub part not continue:\n{}'.format(self))
    
    def __getitem__(self, key):
        if key in self:
            value = super().__getitem__(key)
        else:
            if isinstance(key, int):
                if key>=0:
                    value = self.aslist[self.x_len+key]
                elif key<0:
                    value = self.aslist[key]
                else:
                    raise KeyError("{} isn't valid key or index".format(key))
        return value
    
    def check_used(self):
        for i in self:
            i.check_used()
    
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
        d2 = {'h':BType.month, 'm':BType.minute, 's':BType.second}
        dx = {ABType.date:d1, ABType.time:d2}[self.mtype]
        for key in dx:
            if key in req and dx[key] not in self:
                return False
        return True
       
    def n_unused(self):
        n = 0
        for i in self.aslist:
            if i.check_str_used() == Part.StrUsed.unused:
                n += 1
        return n
    
    def __str__(self):
        ret = 'BigPart:\n'
        for i in self:
            ret += '{}\n'.format(self[i])
        return ret
    
class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        self.used = [False]*len(in_str)
        self.used_parts = BigPart(ABType.subs, inc=False)

    def get_atype(self, re_comp, mtype, stype,
                  filter_used=Part.StrUsed.unused):
        """
        find all use re, atype of sub
        @para re_comp: re.compile object
        @para stype: type_id for Part object
        @para filter_used: only output unused
        """
        founds = re_comp.finditer(self.in_str)
        bpart = BigPart(mtype)
        for i in founds:
            part = Part(self, stype, i.span(), isUse=False)
            if filter_used is None or part.str_used == filter_used:
                bpart[sType.norm] = part
        return bpart
    
    def get_parts(self, re, stype, names):
        mtype = ABType.subs
        ret = {}
        for re_i,stype_i,n_i in zip(re, stype, names):
            ret[n_i] = self.get_atype(re_i, mtype, stype_i)
        return ret
        
    def mark(self, index, num=1):
        if isinstance(index, Iterable) and len(index) == 2:
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
                    ret = Part(self, sType.eng, span)
                else:
                    raise ValueError('found multipy {} in str'.format(err))
        return ret
    
#smart time str to datetime struct
class Time_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)
        self.date_p = BigPart(ABType.date)
        self.time_p = BigPart(ABType.time, used=None)
        self.time_lmrs()
        self.english_month_day()
        self.parts = self.get_parts(re3, sType, sName)
        self.process_num()
    
    def english_month_day(self):
        month = self.find_strs(month_short, 'english month')
        day = self.find_strs(day_short, 'english day')
        if month is not None:
            self.date_p[AType.month] = month
        if day is not None:
            self.date_p[AType.day] = day
    
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
        else:
            return None
    
    def process_num(self):
        for part in self.parts['num'].aslist:
            s = part.span[0]
            e = part.span[1]
            match = part.match()
            inti = int(match)
            if len(match) == 8:
                self.date_p[AType.year] = Part(self, sType.num, (s,   s+4))
                self.date_p[AType.month]= Part(self, sType.num, (s+4, s+6))
                self.date_p[AType.date] = Part(self, sType.num, (s+6, e))
                part.str_used = Part.StrUsed.allused
            elif len(match) == 4:
                if 1970<=inti<2050:
                    self.date_p[AType.year] = Part(self, sType.num, (s, e))
                    part.str_used = Part.IsUsed.allused
                elif 101<=inti<=1231:
                    self.date_p[AType.month]= Part(self, sType.num, (s, s+2))
                    self.date_p[AType.date] = Part(self, sType.num, (s+2, e))
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
        #append Parts to self.time_parts
        self.time_p[BType.left] = Part(self, sType.num, m.span(2))
        self.time_p[sType.norm] = Part(self, sType.num, (m.end(2), m.start(3)))
        if m.group(3) is not None:
            self.time_p[BType.midd] = Part(self, sType.num, (m.start(3),m.end(3)-1))
            self.time_p[sType.norm] = Part(self, sType.num, (m.end(3)-1, m.end(3)))
        self.time_p[BType.right] = Part(self, sType.num, m.span(4))
        if m.group(5) is not None:
            self.time_p[BType.subsec] = Part(self, sType.num, m.span(5))
        #get left, midd, right, subsec
    
    def datetime_process(self):
        if self.date_p.check_finally():
            self.time_p[BType.hours] = self.time_p[BType.left]
            if BType.midd in self.time_p:
                self.time_p[BType.minute] = self.time_p[BType.midd]
                self.time_p[BType.second] = self.time_p[BType.right]
            else:
                assert BType.subsec not in self.time_p
                self.time_p[BType.minute] = self.time_p[BType.right]
        if self.time_p.check_finally():
             pass
         
if __name__ == '__main__':
    test_strs = ['Wed 28/Oct 12:34:56.123', '20201030', '1030', '10:30']
    for i in test_strs:
        print(i)
        tstr = Time_str(i)
        print('date:', tstr.date_p)
        print('time:', tstr.time_p)
        print()
