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


class span(tuple):
    """Span tuple."""

    def __new__(cls, sta, end):
        """Create span tuple."""
        return super().__new__(cls, (sta, end))
    
    def __len__(self):
        return self[1] - self[0]
    
    @property
    def s(self):
        """Get start of span."""
        return self[0]

    @property
    def e(self):
        """Get end of span."""
        return self[1]

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
    def __init__(self, ssn=None, pare=None, nadd=None):
        if ssn is not None:
            self.subset = {} #dict key:name, value:subset(udict)
            for name in ssn:
                self.subset[name] = udict(pareset=self)
        else:
            self.subset = None
        self.pareset = pare
        # if subset not None, forbidden add to self
        if nadd is None:
            nadd = ssn is not None
        self.no_add = nadd
        super().__init__()

    def add(self, part, inner=False):
        if self.no_add and not inner:
            raise RuntimeError('udict read-only, please add to subset')
        ptup = tuple(part)
        if ptup in self.keys():
            raise KeyError('part {} already in set:\n{}'.format(part, self))
        self[ptup] = part
        if self.pareset is not None:
            self.pareset.add(part, inner=True)

    def remove(self, part, rm_pare=True, rm_sub=True):
        if isinstance(part, tuple):
            part = self[part]
        ptup = tuple(part)
        if hasattr(self, 'uiter'):
            self.uiter.skips.add(ptup)
            return
        if ptup in self.keys():
            self.pop(ptup)
        elif (not rm_pare) or (not rm_sub):
            pass
        else:
            raise KeyError('odict remove part: {}'.format(part))
        # remove from subset
        if rm_sub and self.subset is not None:
            for ss in self.subset.values():
                if part in ss:
                    ss.remove(part, rm_pare=False)
        # remove from parent
        if rm_pare and self.pareset is not None:
            self.pareset.remove(part, rm_sub=False)

    def add_subset(self, name, subset):
        assert isinstance(subset, udict)
        for part in subset.values():
            self.add(part, inner=True)
        subset.pareset = self
        self.subset[name] = subset

    def __contains__(self, part):
        if not isinstance(part, Hashable) and isinstance(part, Iterable):
            ptup = tuple(part)
        return super().__contains__(ptup)

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

    def fill(self, date_p, my_odict):
        for lr, plrs in self.items():  #a space can fill
            if lr[1] - lr[0] == len(plrs):
                cp_plrs = plrs.copy()
                key1 = cmp_to_key(lambda x,y:x.part < y.part)
                cp_plrs.sort(key=key1)  #part
                ut_i = lr[0]
                for plr in cp_plrs:
                    date_p[my_odict.klst[ut_i]] = plr.part
                    ut_i += 1
