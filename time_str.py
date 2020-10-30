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
    def __init__(self, mstr, span:tuple, isUse=True):
        self.span = span
        self.mstr = mstr
        self.str_used = self.check_str_used()
        if isUse:
            if self.str_used == Part.StrUsed.unused:
                self.set_str_used()
            else:
                raise ValueError('Part init require isUse, \
but str is {}, not all unused\n\
{}\n{}'.format(self.str_used, self.mstr.in_str, 
' '*span[0]+'^'*(span[1]-span[0])))
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
    
    def check_str_used(self):
        N_used = 0
        for i in range(*self.span):
            if self.mstr.used[i]:
                N_used += 1
        if N_used == 0:
            isUsed = Part.StrUsed.unused
        elif N_used == self.span[1] - self.span[0]:
            isUsed = Part.StrUsed.allused
        else:
            #self.isUsed = Part.IsUsed.partused
            raise ValueError('match part used')
        return isUsed
    
    def set_str_used(self):
        assert self.str_used == Part.StrUsed.unused
        for i in range(*self.span):
            self.mstr.used[i] = True
        self.str_used = Part.StrUsed.allused
    
    def __len__(self):
        return self.span[1] - self.span[0]

#part date or time, can include sub part
class BigPart(dict):
    #TODO: add repart detec
    def __init__(self, mtype, inc=True, cont=False, used=None):
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
        if self.mtype == ABType.date:
            assert key in AType or key is sType.norm
        if self.mtype == ABType.time:
            assert key in BType or key is sType.norm
        if self.mtype != ABType.subs:
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

    
    def __str__(self):
        ret = 'BigPart:\n'
        for i in self.aslist:
            ret += str(i)+'\n'
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
            part = Part(self, i.span(), isUse=False)
            if filter_used is None or part.str_used == filter_used:
                bpart[mtype] = part
        return bpart
    
    def get_parts(self, re, stype, names):
        mtype = ABType.subs
        ret = {}
        for re_i,stype_i,n_i in zip(re, stype, names):
            ret[n_i] = self.get_atype(re_i, mtype, stype_i)
        return ret
        
    def mark(self, index):
        return "{}\n{}^".format(self.in_str, ' '*index)
    
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
        @err: show when find multipy subs
        """
        sub_i = None
        for ni,sub in enumerate(subs):
            index = self.find_onlyone(sub)
            if index != -1:
                span = (index, index+len(sub))
                if sub_i is None:
                    sub_i = ni
                    self.used_parts[None] = Part(self, span)
                else:
                    raise ValueError('found multipy {} in str'.format(err))
        return sub_i, (index, index+len(sub))
    
#smart time str to datetime struct
class Time_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)
        self.date_p = BigPart(ABType.date)
        self.time_p = BigPart(ABType.time, used=None)
        self.T4 = self.time_lmrs()
        self.date = self.date()
        self.parts = self.get_parts(re3, sType, sName)
        self.nums = self.process_num()
    
    def english_month_day(self):
        month, _ = self.find_strs(month_short, 'english month')
        day  , _ = self.find_strs(day_short, 'english day')
        month += 1
        day += 1
        return month, day
    
    def search(self, pattern, start=0, end=-1, isRaise=True, isCheck=True):
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
        return found, (fsta, fend)
    
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
        ret = BigPart(ABType.date)
        for part in self.parts['num'].aslist:
            s = part.span[0]
            e = part.span[1]
            match = part.match()
            inti = int(match)
            if len(match) == 8:
                ret[AType.year] = Part(self, (s,   s+4))
                ret[AType.month]= Part(self, (s+4, s+6))
                ret[AType.date] = Part(self, (s+6, e))
                part.isUsed = Part.StrUsed.allused
            elif len(match) == 4:
                if 1970<=inti<2050:
                    ret[AType.year] = Part(self, (s, e))
                    part.isUsed = Part.IsUsed.allused
                elif 101<=inti<=1231:
                    ret[AType.month]= Part(self, (s, s+2))
                    ret[AType.date] = Part(self, (s+2, e))
                    part.isUsed = Part.IsUsed.allused
        return ret
    
    def time_lmrs(self):
        """
        get time HH:MM:SS.subsec , MM:SS.subsec or HH:MM:SS
        return Left:Midd:Right.subsec
        if not found Midd or subsec, return None
        """
        m, _ = self.search('((\d+):(\d+:)*(\d+)(\.\d+)*)')
        #append Parts to self.time_parts
        self.time_p[BType.left] = Part(self, m.span(2))
        self.time_p[sType.norm] = Part(self, (m.end(2), m.start(3)))
        if m.group(3) is not None:
            self.time_p[BType.midd] = Part(self, (m.start(3),m.end(3)-1))
            self.time_p[sType.norm] = Part(self, (m.end(3)-1, m.end(3)))
        self.time_p[BType.right] = Part(self, m.span(4))
        if m.group(5) is not None:
            self.time_p[BType.subsec] = Part(self, m.span(5))
        #get left, midd, right, subsec
        left = int(m.group(2))
        midd = m.group(3)
        right = int(m.group(4))
        ssec = m.group(5)
        if midd is not None:
            midd = int(midd[:-1])
        if ssec is not None:
            ssec = float(ssec)
        return (left, midd, right, ssec)
    
    def date(self):
        month, day = self.english_month_day()
        return month, day

if __name__ == '__main__':
    test_str = '20200426 Wed 28/Oct 12:34:56.123 '#input('请输入测试字符串:')
    tstr = Time_str(test_str)
    print('test time_lmrs:')
    print(tstr.T4)
    print()
    print('num:', tstr.parts['num'])
    print('eng:', tstr.parts['eng'])
    print('norm:', tstr.parts['norm'])
    print('date:', tstr.nums)
