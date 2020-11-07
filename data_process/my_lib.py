'''
class and func for my_str, time_str
'''
from functools import cmp_to_key
#set for BigPart
class uset(set):
    #TODO: add method remove, check
    #TODO: use dict
    def add(self, ele):
        if ele in self:
            raise KeyError('element {} already in set:\n{}'.format(ele, self))
        super().add(ele)

def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))

class my_odict(dict):
    def __init__(self):
        super().__init__()
        self.klst = []
    def __setitem__(self, k, v):
        if isinstance(k, int):    #k as index
            assert k<len(self.klst)
            k = self.klst[k]
        if k not in self:
            self.klst.append(k)
        super().__setitem__(k, v)
    def __getitem__(self, k):
        if isinstance(k, int):    #k as index
            k = self.klst[k]
        return super().__getitem__(k)
    def get_allow_lr(self, part_obj):
        '''
        prev left ... right next
                part_obj
        
        prev and next are not None
        prev.end <= part_obj.start   and   part_obj.end <= next.start
        left = prev+1
        right = next-1
        
        part_obj can add to left<=x<=right
        '''
        left = None
        right = None
        for ni,k in enumerate(self.klst):
            v = self[k]
            if v is not None:
                if left is None and v < part_obj:
                    left = ni + 1  #prev = v
                if left is not None and right is None and v > part_obj:
                    right = ni - 1 #next = v
                if not any([left,right]): #left and right are not None
                    break
        if left is not None and right is None:
            right = len(self.klst) - 1
        if all([left,right]) and left > right:
            return None
        if not any([left,right]):
            return None
        return left, right
    def next_None(self, ki, prev_next):
        l = len(self.klst)
        ki = {1:0, -1:l-1}[prev_next] if ki is None else ki
        sli = {1:(ki,l,1), -1:(ki,-1,-1)}[prev_next]
        for i in range(*sli):
            if self[self.klst[i]] is None:
                return i
        return sli[1]-prev_next
    def pop():                    #don't delete item
        raise NotImplementedError('my_odict delete is forbidden')

class part_lr:
    def __init__(self, fmt, part, part_i, lr):
        self.fmt = fmt
        self.part = part
        self.part_i = part_i
        self.lr = lr
        self.l = lr[0]
        self.r = lr[1]
    def __lt__(self, other):
        if max(self.l, other.l) > min(self.r, other.r):
            raise RuntimeError('part_lr overlapped')
        return self.l <= other.l or self.r <= other.r
def intersection(i, j):
    sta = max(i.l, j.l)
    end = min(i.r, j.r)
    l = end - sta
    if l>0:  return sta, end
    else:  return None

class parts_insec:
    def __init__(self, part1, part2, insec):
        self.part1 = part1
        self.part2 = part2
        self.insec = insec

class mrange_dict(dict): #dict[Part.tuple] = (Part, l, r)
    def __init__(self, from_dict):
        super().__init__(from_dict)
    
    def fill(self, date_p, my_odict, uuparts_list):
        for lr,plrs in self.items():  #a space can fill
            if lr[1] - lr[0] == len(plrs):
                cp_plrs = plrs.copy()
                key1 = cmp_to_key(lambda x,y:x.part < y.part)
                cp_plrs.sort(key=key1)  #part
                ut_i = lr[0]
                for plr in cp_plrs:
                    date_p[my_odict.klst[ut_i]] = plr.part
                    uuparts_list.remove(plr.part)
                    ut_i += 1
