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
BType = Enum('BType', 'hours minute second subsec ampm')
bType = Enum('bType', 'left midd right')
sType = Enum('sType', 'num eng norm')
#type 0: number  [0-9]
#type 1: english [A-Za-z]
#type 2: chara   -:,/  <space>
#type 3: other

class Part():
    IsUsed = Enum('IsUsed', 'unused partused allused')
    def __init__(self, mstr, stype, span:tuple):
        self.span = span
        self.mstr = mstr
        self.stype = stype
        self.check_used()
        
    def match(self):
        return self.mstr.in_str[self.span[0]:self.span[1]]
    
    def __str__(self):
        ret = 'span={} str="{}", isUsed={}, stype={}'\
        .format(self.span, self.mstr.in_str[self.span[0]:self.span[1]], 
                self.isUsed, self.stype)
        return ret
    
    def __lt__(self, other):
        return self.span[0] < other.span[0]
    
    def check_used(self):
        N_used = 0
        for i in range(*self.span):
            if self.mstr.used[i]:
                N_used += 1
        if N_used == 0:
            self.isUsed = Part.IsUsed.unused
        elif N_used == self.span[1] - self.span[0]:
            self.isUsed = Part.IsUsed.allused
        else:
            #self.isUsed = Part.IsUsed.partused
            raise ValueError('match part used')
    
    def __len__(self):
        return self.span[1] - self.span[0]

#part date or time, can include sub part
class BigPart(list):
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
        
    def append(self, obj):
        super().append(obj)
        if self.used is not None and self.used != obj.isUsed:
            raise ValueError('used reqire is not same')
        if len(self)>=2:
            if self.inc and self[-2] > self[-1]:
                raise ValueError('sub part not increase')
            if self.cont and self[-2] != self[-1]:
                raise ValueError('sub part not continue')
    
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
        ret = ''
        for i in self:
            ret += str(i)+'\n'
        return ret
    
class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        self.used = [False]*len(in_str)
        self.used_parts = []

    def get_atype(self, re_comp, mtype, stype, filter_used=Part.IsUsed.unused):
        """
        find all use re, atype of sub
        @para re_comp: re.compile object
        @para stype: type_id for Part object
        @para filter_used: only output unused
        """
        founds = re_comp.finditer(self.in_str)
        bpart = BigPart(mtype)
        for i in founds:
            part = Part(self, mtype, i.span())
            if filter_used is None or part.isUsed == filter_used:
                bpart.append(part)
        return bpart
    
    def get_parts(self, re, stype, names):
        mtype = ABType.subs
        ret = {}
        for re_i,stype_i,n_i in zip(re, stype, names):
            ret[n_i] = self.get_atype(re_i, mtype, stype_i)
        return ret
    
    def set_used(self, stype, start, end=None):
        if end == None:
            end = start + 1
        for i in range(start, end):
            if self.used[i] == True:
                raise ValueError('in_str[{}] is already used\n{}'
                                 .format(i, self.mark(i)))
            self.used[i] = True
        self.used_parts.append(Part(self, stype, (start, end)))
        
    def mark(self, index):
        return "{}\n{}^".format(self.in_str, ' '*index)
    
    def findall(self, sub):
        """
        find all sub str.
        @para sub: the sub str
        @return: list of found indexs
        """
        start = 0
        ret = []
        while True:
            index = self.in_str.find(sub, start)
            if index != -1:
                ret.append(index)
                self.set_used(index, index+len(sub))
                start = index + len(sub)
            else:
                return ret
    
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
                if sub_i is None:
                    sub_i = ni
                    self.set_used(sType.eng, index, index+len(sub))
                else:
                    raise ValueError('found multipy {} in str'.format(err))
        return sub_i, (index, index+len(sub))

class info:
    #TODO: remove
    def __init__(self, itype, from_stype, value):
        self.itype = itype
        self.from_stype = from_stype
        self.value = value
        
#smart time str to datetime struct
class Time_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)
        self.date_p = BigPart(ABType.date)
        self.time_p = BigPart(ABType.time, used=None)
        self.T4 = self.time_lmrs()
        self.date = self.date()
        self.parts = self.get_parts(re3, sType, sName)
        self.process_num()
    
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
        self.set_used(3, fsta, fend)
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
        #TODO remove info, use date_p
        ret = []
        for i in self.parts['num']:
            match = i.match()
            inti = int(match)
            if len(match) == 8:
                year = inti[:4]
                month = inti[4:6]
                date = inti[6:]
                ret.append(info(AType.year, sType.num, year))
                ret.append(info(AType.month,sType.num, month))
                ret.append(info(AType.date, sType.num, date))
            elif len(match) == 4:
                if 1970<=inti<2050:
                    year = inti
                    ret.append(info(AType.year, sType.num, year))
                elif 101<=inti<=1231:
                    month = int(inti[:2])
                    date = int(inti[2:])
                    ret.append(info(AType.month, sType.num, month))
                    ret.append(info(AType.date,  sType.num, date))
    
    def time_lmrs(self):
        """
        get time HH:MM:SS.subsec , MM:SS.subsec or HH:MM:SS
        return Left:Midd:Right.subsec
        if not found Midd or subsec, return None
        """
        m, _ = self.search('((\d+):(\d+:)*(\d+)(\.\d+)*)')
        #append Parts to self.time_parts
        self.time_p.append(Part(self, bType.left, m.span(2)))
        self.time_p.append(Part(self, sType.norm, (m.end(2), m.start(3))))
        if m.group(3) is not None:
            self.time_p.append(Part(self, bType.midd, (m.start(3),m.end(3)-1)))
            self.time_p.append(Part(self, sType.norm, (m.end(3)-1, m.end(3))))
        self.time_p.append(Part(self, bType.right, m.span(4)))
        if m.group(5) is not None:
            self.time_p.append(Part(self, BType.subsec, m.span(5)))
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
    test_str = '2020 Wed 28/Oct 12:34:56.123 '#input('请输入测试字符串:')
    tstr = Time_str(test_str)
    print('test time_lmrs:')
    print(tstr.T4, tstr.date)
    print('num:', tstr.parts['num'])
    print('eng:', tstr.parts['eng'])
    print('norm:', tstr.parts['norm'])
