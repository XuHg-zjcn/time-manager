'''
class and func for my_str, time_str
'''
from collections import Hashable


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

    def len_ab(self):
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
        except StopIteration:     # after iteration, remove skips
            del self.ud.uiter
            for skip in self.skips:
                self.ud.remove(skip)
            raise StopIteration
        return n[1]


class udict(dict):
    def __init__(self, ssn=None, pare=None, nadd=None, check_add=True):
        if ssn is not None:
            self.subset = {}  # dict key:name, value:subset(udict)
            for name in ssn:
                self.subset[name] = udict(pareset=self)
        else:
            self.subset = None
        self.pareset = pare
        # if subset not None, forbidden add to self
        if nadd is None:
            nadd = ssn is not None
        self.no_add = nadd
        self.check_add = check_add
        super().__init__()

    def add(self, part, inner=False):
        if self.no_add and not inner:
            raise RuntimeError('udict read-only, please add to subset')
        ptup = tuple(part)
        if self.check_add and ptup in self.keys():
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
        if not isinstance(part, Hashable):
            ptup = tuple(part)
        return super().__contains__(ptup)

    def __iter__(self):   # iter dict value(Part objs)
        self.uiter = uiter(self.items().__iter__(), self)
        return self.uiter


def strictly_increasing(L):
    return all(x<y for x,y in zip(L, L[1:]))
