import re
from enum import Enum
from collections import Iterable
from my_lib import udict

re_num = re.compile('\d+')
re_eng = re.compile('[a-zA-Z]+')
re_norm = re.compile('[-:,/ ]+')

nums = '0123456789'
engs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
norms= '-:.,/\ '
sType = Enum('sType', 'num eng norm other')
sType2exam = {sType.num:nums,   sType.eng:engs,   sType.norm:norms}
sType2re_c = {sType.num:re_num, sType.eng:re_eng, sType.norm:re_norm}

#a Part of str, can add to BigPart or UnusedParts
class Part():
    StrUsed = Enum('IsUsed', 'unused partused allused')
    def __init__(self, mstr, span:tuple,
                 stype=None, value=None):
        self.span = span
        self.mstr = mstr
        self.stype = self.check_stype(stype)
        self.value = self.get_value(value)
        self.flags = set()
    
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
    
    def get_value(self, v):
        s = self.match_str()
        if v == 'no find':
            value = None
        elif self.stype == sType.num:
            if s[0] == '.':
                value = float(s)
            else:
                value = int(s)
            if v is not None:
                assert value == v
        else:
            value = v
        return value
    
    def __str__(self):
        if type(self.value) in (int, float) or self.value is None:
            str_value = str(self.value)
        else:
            raise ValueError("self.value isn't int, float or None")
        ret = 'span={:>7}, str="{}", value={}'\
        .format(str(self.span), self.mstr.in_str[self.span[0]:self.span[1]],
                str_value)
        return ret
    
    def __eq__(self, other):
        return self.mstr == other.mstr and \
               self.span == other.span
    
    def __lt__(self, other):
        return self.span[1] <= other.span[0]
    
    def __gt__(self, other):
        return other.span[1] <= self.span[0]
    
    def __len__(self):
        return self.span[1] - self.span[0]
    
    def __iter__(self):
        return self.span.__iter__()
    
    def set_str_used(self):
        self.mstr.set_str_used(self.span)

#part date or time, can include sub part
class BigPart(dict):
    def __init__(self, mstr, name, key_allow):
        '''
        @para inc: all sub parts increase, next part head after prev end.
        @para cont: all sub parts continuous, next part head close prev end.
        @para used: None not any, True is unused, False is allused
        
        dict's key: sType.norm or UType.xxx
        dict's value: Part object
        '''
        super().__init__()
        self.mstr = mstr
        self.name= name
        self.span = None
        self.part_objs = [] #each item is Part object
        self.key_allow = key_allow
        
    def __setitem__(self, key, value):
        assert isinstance(value, Part)
        if key != sType.norm:
            #check key vaild for BigPartType
            if key not in self.key_allow:
                raise KeyError('key {} is invalid for BigPart {}'
                               .format(key, self.name))
            #check key is not using
            if key in self:
                raise KeyError('key {} is already in BigPart {} dict'
                               .format(key, self.name))
            super().__setitem__(key, value)
        else:
            self.part_objs.append(value)
         #Part obj in UnusedParts poped
        if value in self.mstr.unused_parts:
            self.mstr.unused_parts.remove(value)
        #Part obj in BigPart poped
        if 'BigPart poped' in value.flags:
            value.flags.remove('BigPart poped')
        else:
            self.mstr.part_set.add(value)
            value.set_str_used()
            
        #update self.span
        if self.span is None:
            self.span = list(value.span)
        else:
            if value.span[0] < self.span[0]: #Part's left point over BigPart
                self.span[0] = value.span[0]
            if value.span[1] > self.span[1]: #Part's right point over BigPart
                self.span[1] = value.span[1]
        if value.value is None:
            value.value = value.get_value(None)
    
    def pop(self, key):
        part = super().pop(key)
        part.flags.add('BigPart poped')
        return part
    
    def check_breakpoint(self):
        '''
        check is middle broken, 
        such as found HH::SS without minute, YYYY//DD without month
        return True is not broken, False have probem
        '''
        keys = list(self.keys())
        k_cls = map(lambda x:x.__class__, keys) #value of Enum
        try:
            kcls1 = next(k_cls)
        except StopIteration:
            return
        for i in k_cls:
            assert i == kcls1
        key_v = list(map(lambda x:x.value, keys)) #value of Enum
        key_v.sort()
        if len(key_v) >= 2:
            for i0,i1 in zip(key_v, key_v[1:]):
                if i0+1 != i1:
                    key_n = list(map(lambda x:x.name, keys)) #name of Enum
                    raise ValueError('found keys:{}, but not {}'
                                     .format(key_n, kcls1(i1)))
    
    def check_unused_char(self, allow, disallow):
        if self.span is not None:
            self.mstr.check_unused_char(allow, disallow, self.span)
    
    def __str__(self):
        if len(self) != 0:
            ret = '-----------------------------------\n'
            for i in self:
                ret += '{:<7}:{}\n'.format(i.name, self[i])
            ret = ret[:-1]
            return ret
        else:
            return 'empty------------------------------'

class My_str:
    def __init__(self, in_str):
        self.in_str = in_str
        #only modify in BigPart.__setitem__ through set_str_used
        self.used = [False]*len(in_str)
        self.disallow_unused_chars = ''
        self.part_set = udict()                    #for two BigPart
        self.unused_parts = udict(subset_names=[]) #for all UnusedParts obj
    
    def get_allsType_parts(self, sType2re_c):
        """
        find a group re_compile
        @para sType2re_c: a dict key:sType, value:re.compile obj
        """
        def get_atype(self, re_comp, stype,
                      filter_used=Part.StrUsed.unused):
            """
            find all use re, atype of sub
            @para re_comp: re.compile object
            @para stype: type_id for Part object
            @para filter_used: only output unused
            """
            founds = re_comp.finditer(self.in_str)
            ud = udict()
            for i in founds:
                str_used = self.is_str_used(i.span())
                if filter_used is None or str_used == filter_used:
                    part = Part(self, i.span(), stype, value='no find')
                    ud.add(part)
            return ud
        
        for stype, re_i in sType2re_c.items():
            self.unused_parts.add_subset(
                stype.name, get_atype(self, re_i, stype))
        
    def mark(self, index, num=1, out_str=True):
        if isinstance(index, Iterable) and len(index) == 2:
            num = index[1] - index[0]
            index = index[0]
        elif isinstance(index, int):
            pass
        else:
            raise ValueError('index must len=2 or int')
        #geterate
        ret = ''
        if out_str:
            ret += self.in_str + '\n'
        N_end_space = len(self.in_str)-index-num
        if N_end_space < 0:
            raise IndexError('end of mark out of range')
        ret += ' '*index+'^'*num+' '*N_end_space
        return ret
    
    def find_strs(self, subs, puls1):
        """
        find which sub in in_str, only one sub can find, else raise ValueError
        @para subs: list of subs
        @para err: show when find multipy subs
        @ret sub_i: the index of sub, when found the Part
        @ret ret_Part: found Part
        """
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
        
        ret = None
        for ni,sub in enumerate(subs):
            index = find_onlyone(self, sub)
            if index != -1:
                span = (index, index+len(sub))
                if ret is None:
                    value = ni+1 if puls1 else ni
                    ret = Part(self, span, sType.eng, value=value)
                else:
                    raise ValueError('found multipy in str')
        return ret
    
    def search(self, re_comp, start=0, end=None, isRaise=True, isCheck=True):
        found = re_comp.search(self.in_str[start:end])
        if found is None:
            if isRaise:
                raise ValueError('search re not found')
            else:
                return None
        return found
    
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
    
    def check_unused_char(self, allow, disallow, search_span=None):
        '''
        if char'O' in allow or disallow, as the defalut other,
        don't add other char if 'O' in str, is invaild
        char not in both allow and disallow, add to disallow for later call.
        '''
        class oset(set):
            def __init__(self, set0):
                super().__init__(set0)
            def __contains__(self, x):
                return not super().__contains__(x)
        if search_span is None:
            search_span = (0, len(self.in_str))
        #get allow and disallow set
        allow = set(allow)
        disallow = set(disallow)
        assert set.isdisjoint(allow, disallow)
        other_allow    = 'O' in allow
        other_disallow = 'O' in disallow
        if other_allow:   #clear if 'O' in regular str
            allow = oset(disallow)
        if other_disallow:
            disallow = oset(allow)
        #get unused_span_list: used flag of char is False spans
        unused_span_list = []
        last_span = [0,0]
        last_use = self.used[search_span[0]] #TODO: use zip
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
                                 .format(self.mark(span)))
            else:
                i = span[0]
                assert span[1] == i+1
                c = self.in_str[i]
                if c in allow:
                    self.set_str_used(span)
                elif c in disallow:
                    raise ValueError('in call disallow unused char\n{}'
                                 .format(self.mark(i)))
                elif c in self.disallow_unused_chars:
                    raise ValueError('in My_str disallow unused char\n{}'
                                 .format(self.mark(i)))
                else:
                    #disable for later call
                    self.disallow_unused_chars += c
    
    def print_str_use_status(self, mark):
        assert mark in {'^', 'v', '.'}
        marks = ''
        n_used = 0
        for used_i in self.used:
            marks += {False:' ', True:mark}[used_i]
            n_used += used_i
        len_str = len(self.in_str)
        unused = len_str - n_used
        if mark == '^':
            print('str:|{}|\n     {}'.format(self.in_str, marks))
        else:
            print('     {}\nstr:|{}|'.format(marks, self.in_str))
        print('str use status: total={}, used={}, unused={}'
              .format(len_str, n_used, unused))
