'''
class and func for my_str, time_str
'''
from collections import Hashable, Iterable
# from functools import wraps

class oset(set):
    def __init__(self, set0):
        super().__init__(set0)

    def __contains__(self, x):
        return not super().__contains__(x)


class span(tuple):
    """Span tuple."""

    def __new__(cls, sta, end=None):
        """Create span tuple."""
        if isinstance(sta, Iterable):
            assert len(sta) == 2
            end = sta[1]
            sta = sta[0]
        assert sta <= end
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

    @property
    def sta(self):
        """Get start of span."""
        return self[0]

    @property
    def end(self):
        """Get end of span."""
        return self[1]

    def __contains__(self, num):
        return self[0] <= num < self[1]

    def __add__(self, num):
        if isinstance(num, int) or isinstance(num, float):
            sta2 = self.sta + num
            end2 = self.end + num
            return span(sta2, end2)
        else:
            raise TypeError('span add num unsupport type')

    def __sub__(self, obj_num):
        """If obj is span, return diff; obj is number, sub to start and end."""
        if isinstance(obj_num, int) or isinstance(obj_num, float):
            sta = self.sta - obj_num
            end = self.end - obj_num
            return span(sta, end)
        elif isinstance(obj_num, span):
            sp0 = span(self.sta, min(self.end, obj_num.sta))
            sp1 = span(min(self.sta, obj_num.end), self.end)
            return sp0 + sp1
        else:
            raise TypeError('span sub unsupport type')

    def __mul__(self, num):
        if isinstance(num, int) or isinstance(num, float):
            return span(self.sta*num, self.end*num)
        else:
            raise TypeError('span mul num unsupport type')

    def __truediv__(self, obj):
        if isinstance(obj, int) or isinstance(obj, float):
            return span(self.sta/obj, self.end/obj)
        else:
            raise TypeError('span div num unsupport type')

    def as_int(self):
        return span(int(self.sta), int(self.end))

    def __and__(self, obj):
        if isinstance(obj, span):
            sta3 = max(self.sta, obj.sta)
            end3 = min(self.end, obj.end)
            if sta3 <= end3:
                return span(sta3, end3)
            else:
                return None
        else:
            raise TypeError('span logic and unsupport type')

    def __or__(self, obj):
        if isinstance(obj, span):
            if obj.s <= self.e or self.s <= obj.e:   # has overlap
                sta3 = min(self.sta, obj.sta)
                end3 = max(self.end, obj.end)
                return span(sta3, end3)
            else:    # no overlap
                return Spans([self, obj])
        else:
            raise TypeError('span logic or unsupport type')

    def __xor__(self, obj):
        if isinstance(obj, span):
            sta3 = max(self.sta, obj.end)
            end3 = min(self.end, obj.sta)
            sta4 = max(obj.sta, self.end)
            end4 = min(obj.end, self.sta)
            if sta3 <= end3 and sta4 <= end4:
                return Spans(span(sta3, end3), span(sta4, end4))
            elif sta3 <= end3:
                return span(sta3, end3)
            elif sta4 <= end4:
                return span(sta4, end4)
            else:
                return None
        else:
            raise TypeError('span logic xor unsupport type')

class Spans(list):
    def __init__(self, iterable=[]):
        super().__init__()
        if len(iterable) == 0:
            return
        iter0 = iterable[0]
        if isinstance(iter0, bool):        # each is bool
            sp = [0, 0]
            for i, pre, nex in zip(range(len(iterable)-1),
                                   iterable, iterable[1:]):
                if pre is False and nex is True:
                    sp[0] = i
                elif pre is True and nex is False:
                    sp[1] = i
                    self.append(span(sp))
        elif isinstance(iter0, Iterable):   # each is span
            for sp in iterable:
                assert len(sp) == 2
                self.append(span(sp))
        elif isinstance(iter0, span):
            for sp in iterable[1:]:
                assert isinstance(sp, span)
            return self
        else:
            raise TypeError('spans init by type {} not allow'
                            .format(type(iterable)))

    def append(self, sp):
        if isinstance(sp, span):
            super().append(sp)
        elif isinstance(sp, tuple) and len(sp) == 2:
            super().append(span(sp))
        elif isinstance(sp, Spans):
            self += sp
        else:
            raise TypeError('spans append type {} not allow'.format(type(sp)))

    def merge_insec(self, merge=True):
        self.sort(key=lambda x: x[0])
        rm = []
        for i, (_,le), (ns,_) in zip(range(len(self)-1), self, self[1:]):
            if le > ns:
                if not merge:
                    return False
                sta3 = self[i].sta
                end3 = self[i+1].end
                self[i+1] = span(sta3, end3)
                rm.append(i)
        for rm_i in rm[::-1]:
            self.spans.pop(rm_i)
        return len(rm) == 0    # no remove True

    def __contains__(self, num):
        assert isinstance(num, int) or isinstance(num, float)
        for sp in self.spans:
            if num in sp:
                return True
        return False

    def _apply_each_span(func):
        def wrapper(self, obj, **kwargs):
            if isinstance(obj, int) or isinstance(obj, float):
                return Spans(list(map(lambda x: func(x, obj), self)))
            elif isinstance(obj, span):
                ret = Spans()
                for sp in self:
                    aped = func(sp, obj)
                    if aped is not None:
                        ret.append(func(sp, obj))
                return ret
            else:
                raise TypeError('spans append type {} not allow'
                                .format(type(sp)))
        return wrapper

    @_apply_each_span
    def __add__(self, num):
        return self + num

    @_apply_each_span
    def __sub__(self, num):
        return self - num

    @_apply_each_span
    def __mul__(self, obj_num):
        return self * obj_num

    @_apply_each_span
    def __truediv__(self, num):
        return self / num

    def as_int(self):
        return Spans(list(map(lambda x: x.as_int(), self)))

    @_apply_each_span
    def __and__(self, obj):
        return self & obj

    @_apply_each_span
    def __or__(self, obj):
        return self | obj

    @_apply_each_span
    def __xor__(self, obj):
        return self ^ obj


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
