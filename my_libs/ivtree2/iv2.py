#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from .ivtree2 import IvTree2

class Iv2(Interval):
    def __contains__(self, num):
        return self.contains_point(num)

    def __add__(self, num):
        """Add number to begin and end."""
        return Iv2(self.begin+num, self.end+num, self.data)

    def __sub__(self, num):
        """Sub number to begin and end."""
        return Iv2(self.begin-num, self.end-num, self.data)

    def __mul__(self, num):
        """Multply number to begin and end."""
        return Iv2(self.begin*num, self.end*num, self.data)

    def __truediv__(self, num):
        """Truediv number to begin and end."""
        return Iv2(self.begin/num, self.end/num, self.data)

    def __floordiv__(self, num):
        """Floordiv number to begin and end."""
        return Iv2(self.begin//num, self.end//num, self.data)

    def __neg__(self):
        """Get negative begin and end."""
        return Iv2(-self.begin, -self.end, self.data)

    def __repr__(self):
        """
        Executable string representation of this Interval.
        :return: string representation
        :rtype: str
        """
        if isinstance(self.begin, Number):
            s_begin = str(self.begin)
            s_end = str(self.end)
        else:
            s_begin = repr(self.begin)
            s_end = repr(self.end)
        if self.data is None:
            return "Iv2({0}, {1})".format(s_begin, s_end)
        else:
            return "Iv2({0}, {1}, {2})".format(s_begin, s_end, repr(self.data))

    def __and__(self, other):
        """Intersection Interval.

        if not overlap, return None.
        :param other: an interval
        :rtype: Optional[Iv2, IvTree2]
        """
        begin = max(self.begin, other.begin)
        end = min(self.end, other.end)
        if begin < end:
            return Iv2(begin, end, self.data)
        else:
            return None

    def __or__(self, other):
        """Union Interval.

        if not overlap, return both in tree.
        :param other: an interval
        :return: combination intervals
        :rtype: Optional[Iv2, IvTree2]
        """
        if self.overlaps(other):
            begin = min(self.begin, other.begin)
            end = max(self.end, other.end)
            return Iv2(begin, end, self.data)
        else:
            return IvTree2([self, other])

    def __xor__(self, other):
        """Xor logic."""
        sta3 = max(self.begin, other.end)
        end3 = min(self.end, other.begin)
        sta4 = max(other.begin, self.end)
        end4 = min(other.end, self.begin)
        if sta3 <= end3 and sta4 <= end4:
            return IvTree2([Iv2(sta3, end3), Iv2(sta4, end4)])
        elif sta3 <= end3:
            return Iv2(sta3, end3)
        elif sta4 <= end4:
            return Iv2(sta4, end4)
        else:
            return None

    def __invert__(self):
        """Invert intervals.

        :return: interval intervals [(-inf, begin), (end, inf)]
        :rtype: IvTree2
        """
        left = Iv2(float('-inf'), self.begin, self.data)
        right = Iv2(self.end, float('inf'), self.data)
        return IvTree2([left, right])

    __str__ = __repr__
