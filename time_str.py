import datetime
import re

day_full=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
day_short=['Mon','Tue','Wed','Thur','Fri','Sat','Sun']
month_full=['January','February','March','April','May','June','July','August','Spetember','October','November','December']
month_short=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Spet','Oct','Nov','Dec']
#type 0: number  [0-9]
#type 1: english [A-Za-z]
#type 2: chara   -:,/  <space>
#type 3: other

class Part():
    def __init__(self, match, stype):
        self.match = match
        self.stype = stype
    
    def __lt__(self, other):
        return self.match.start() < other.match.start()

class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        self.used = [False]*len(in_str)

    #unused
    def get_atype(self, re_comp, stype):
        """
        find all use re, atype of sub
        @para re_comp: re.compile object
        @para stype: type_id for Part object
        """
        found = re_comp.finditer(self.in_str)
        found = map(lambda x:Part(x, stype), found)
        print(found)
        found = list(found)
        return found
    
    def set_used(self, start, end=None):
        if end == None:
            end = start + 1
        for i in range(start, end):
            if self.used[i] == True:
                raise ValueError('in_str[{}] is already used\n{}'.format(i, self.mark(i)))
            self.used[i] = True
        
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
        index_range = None
        for sub_i,asub in enumerate(subs):
            index = self.find_onlyone(asub)
            if index != -1:
                if sub_i is None:
                    sub_i = ni+1
                    index_range = (index, index+len(asub))
                    set_used(*index_range)
                else:
                    raise ValueError('found multipy {} in str'.format(err))
        return sub_i, index_range

#smart time str to datetime struct
class Time_str(My_str):
    re_num = re.compile('\d+')
    re_eng = re.compile('[a-zA-Z]+')
    re_norm = re.compile('[-:,/ ]+')
    def __init__(self, in_str):
        super().__init__(in_str)
        #self.get_parts()
    
    #unused
    def get_parts(self):
        self.num_parts = self.get_atype(Time_str.re_num, 0)
        self.eng_parts = self.get_atype(Time_str.re_eng, 1)
        self.norm_parts= self.get_atype(Time_str.re_norm,2)
        parts = self.num_parts + self.eng_parts + self.norm_parts
        self.parts = parts.sort()
    
    def english_month_day(self):
        month, _ = self.find_strs(month_short, 'english month')
        day  , _ = self.find_strs(day_short, 'english day')
        return month, day
    
    def search(self, pattern, start=0, end=-1, isRaise=True):
        found = re.search(pattern, self.in_str[start:end])
        if found is None:
            if isRaise:
                raise ValueError('search re pattern"{}" not found'.format(pattern))
            else:
                return None
        fsta = start+found.start()
        fend = start+found.end()
        self.set_used(fsta, fend)
        if pattern[0] != '^':
            self.check_spilt(fsta-1)
        if pattern[-1]!= '$':
            self.check_spilt(fend)
        return found
    
    def check_spilt(self, index, other_allow=[], isRaise=True):
        if 0<=index<len(self.in_str):
            char = self.in_str[index]
            spilt = [' ', '|', '.'] + other_allow
            if char not in spilt and isRaise:
                raise ValueError("'{}' not in avabile spilt character{}\n{}"\
                .format(char, spilt, self.mark(index)))
            return char
        else:
            return None
    
    def time_lmrs(self):
        """
        get time HH:MM:SS.subsec , MM:SS.subsec or HH:MM:SS
        return Left:Midd:Right.subsec
        if not found Midd or subsec, return None
        """
        match = self.search('(\d+):(\d+:)*(\d+)(\.\d+)*')
        left = int(match.group(1))
        midd = match.group(2)
        right = int(match.group(3))
        subs = match.group(4)
        if midd is not None:
            midd = int(midd[:-1])
        if subs is not None:
            subs = float(subs)
        return (left, midd, right, subs)

if __name__ == '__main__':
    test_str = ' 12:34:56.123 '#input('请输入测试字符串:')
    tstr = Time_str(test_str)
    T4 = tstr.time_lmrs()
    print('test time_lmrs:')
    print(T4)
