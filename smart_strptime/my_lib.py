'''
class and func for my_str, time_str
'''
from functools import cmp_to_key
from collections import Hashable, Iterable

class oset(set):
    def __init__(self, set0):
        super().__init__(set0)
    def __contains__(self, x):
        return not super().__contains__(x)

class uiter:
    def __init__(self, iter_from, ud):
        self.skips = set()
        self.iter_from = iter_from
        self.ud = ud
    def __next__(self):
        try:
            n = next(self.iter_from)
        except StopIteration:     #after iteration, remove skips
            del self.ud.uiter
            for skip in self.skips:
                self.ud.remove(skip)
            raise StopIteration
        if n[0] in self.skips:
            return next(self)
        return n[1]

class udict(dict):        
    uflag = 'udict inner'
    def __init__(self, subset_names=None, pareset=None, read_only=False):
        if subset_names is not None:
            self.subset = {} #dict key:name, value:subset(udict)
            for name in subset_names:
                self.subset[name] = udict(pareset=self)
        else:
            self.subset = None
        self.pareset = pareset
        self.read_only = read_only
        super().__init__()
        self.flags = set()
    
    def ro_test(self, part):
        has_uflag = udict.uflag in part.flags
        if has_uflag:
            part.flags.remove(udict.uflag)
        if self.read_only and (not has_uflag):
            raise RuntimeError('udict read-only, please add to subset')
    
    def apply_pare(self, fn, part):
        if self.pareset is not None:
            part.flags.add(udict.uflag)
            getattr(self.pareset, fn)(part)
    
    def add(self, part):
        self.ro_test(part)
        ptup = tuple(part)
        if ptup in self.keys():
            raise KeyError('part {} already in set:\n{}'.format(part, self))
        self[ptup] = part
        self.apply_pare('add', part)

    
    def remove(self, part):
        if isinstance(part, tuple):
            part = self[part]
        ptup = tuple(part)
        self.ro_test(part)
        if hasattr(self, 'uiter'):
            self.uiter.skips.add(ptup)
            return
        self.pop(ptup)
        if self.subset is not None:
            for ss in self.subset.values():
                part.flags.add(udict.uflag)
                part.flags.add('udict subset')
                try:
                    ss.remove(part)
                except Exception: pass
                else:             break
        if 'udict subset' not in part.flags:
            self.apply_pare('remove', part)
        else:
            part.flags.remove('udict subset')
    
    def add_subset(self, name, subset):
        assert isinstance(subset, udict)
        self.subset[name] = subset
        for i in subset:
            self.add(i)
    
    def __contains__(self, obj):
        if not isinstance(obj, Hashable) and isinstance(obj, Iterable):
            obj = tuple(obj)
        return super().__contains__(obj)
    
    def __iter__(self):  #iter dict value(Part objs)
        self.uiter = uiter(self.items().__iter__(), self)
        return self.uiter

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
    def __init__(self, fmt, part, lr):
        self.fmt = fmt
        self.part = part
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

class mrange_dict(dict): #dict[Part.tuple] = [plr1, plr2]
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
                    ut_i += 1
