"""
Copyright 2020 Xu Ruijun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from numbers import Number
from intervaltree import Interval
from intervaltree import IntervalTree
from .iv2 import Iv2


class IvTree2(IntervalTree):
    def apply_each_interval(self, func):
        ret = IvTree2()
        for iv in self:
            begin = func(iv.begin)
            end = func(iv.end)
            if begin < end:
                ret.addi(begin, end, iv.data)
        return ret

    def copy(self):
        return IvTree2(iv.copy() for iv in self)

    def __add__(self, num):
        """Add number to begin and end each interval."""
        return self.apply_each_interval(lambda x: x+num)

    def _sub_num(self, num):
        return self.apply_each_interval(lambda x: x-num)

    def __sub__(self, ivt_num):
        """Sub number to begin and end each interval, or get difference set."""
        if isinstance(ivt_num, IntervalTree) or isinstance(ivt_num, Interval):
            return self.copy()._chops(ivt_num)
        elif isinstance(ivt_num, Number):
            return self._sub_num(ivt_num)

    def __mul__(self, num):
        """Multply number to begin and end each interval."""
        return self.apply_each_interval(lambda x: x*num)

    def __truediv__(self, num):
        """Truediv number to begin and end each interval."""
        return self.apply_each_interval(lambda x: x/num)

    def __floordiv__(self, num):
        """Floordiv number to begin and end each interval."""
        return self.apply_each_interval(lambda x: x//num)

    def notx(self, use_data='right', use_inf=True):
        """
        Invert intervals.
        overlaps on original tree will merge.

        :para data: 'right' use right side data, 'left' use left side data,
                    'none' for no data
        :para use_inf: True will keep -inf and inf two side, False don't use inf.
        """
        ret = IvTree2()
        last_end = float('-inf')
        assert use_data in ['left', 'right', 'none']
        last_data = None
        cp = self.copy()
        if use_data == 'left':
            data_reducer = lambda a,b: a
        elif use_data == 'right':
            data_reducer = lambda a,b: b
        else:
            data_reducer = None
        cp.merge_overlaps(data_reducer)
        sort = sorted(cp)
        if not use_inf:
            i0 = sort.pop(0)
            last_end = i0.end
            last_data = i0.data
        for iv in sort:
            if use_data == 'left':
                data = last_data
                last_data = iv.data
            elif use_data == 'right':
                data = iv.data
            else:  # use_data == 'none'
                data = None
            ret.addi(last_end, iv.begin, data)
            last_end = iv.end
        if use_inf:
            ret.addi(last_end, float('inf'), last_data)
        return ret

    def __invert__(self):
        """Invert intervals."""
        return self.notx(use_data='right', use_inf=True)

    def __and__(self, other):
        """Chop range not in other, data will keep left side."""
        # chooise less intervals item as base
        if isinstance(other, IntervalTree) and len(self) < len(other):
            ret = IvTree2(other.overlap(self.begin(), self.end()))
            ret._chops(~self)
        else:
            if isinstance(other, Interval):
                o_begin = other.begin
                o_end = other.end
                if not isinstance(other, Iv2):
                    other = Iv2(other)
            elif isinstance(other, IntervalTree):
                o_begin = other.begin()
                o_end = other.end()
            else:
                raise TypeError('unsupported type', type(other))
            ret = IvTree2(self.overlap(o_begin, o_end))
            ret._chops(~other)
        return ret

    def __iand__(self, other):
        """In some time fast."""
        self._chops(~other)
        return self

    def __ior__(self, other):
        """In some time fast."""
        self.update(other)
        self.merge_overlaps()
        return self

    def __or__(self, other):
        """Merge other, data will None if overlap."""
        ret = self.copy()
        ret.update(other)
        ret.merge_overlaps()
        return ret

    def __xor__(self, other):
        """Xor logic, probably slow."""
        return self - self & other

    def _chops(self, other):
        """
        Chop range in other, data will keep self.

        please use ivtree - ivtree or ivitem.
        """
        if isinstance(other, IntervalTree):
            for iv in sorted(other):
                self.chop(iv.begin, iv.end)
        elif isinstance(other, Interval):
            self.chop(other.begin, other.end)

    def __repr__(self):
        """
        :rtype: str
        """
        ivs = sorted(self)
        if not ivs:
            return "IvTree2()"
        else:
            return "IvTree2({0})".format(ivs)

    __str__ = __repr__

    def map_data(self, func):
        ret = IvTree2()
        for iv in self:
            ret[iv.begin:iv.end] = func(iv.data)
        return ret
