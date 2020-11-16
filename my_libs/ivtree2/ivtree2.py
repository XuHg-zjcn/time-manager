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
from intervaltree import IntervalTree

class IvTree2(IntervalTree):
    def apply_each_interval(self, func):
        ret = IvTree2()
        for iv in self:
            ret.addi(func(iv.begin),
                     func(iv.end),
                     iv.data)
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

    def notx(self, use_data='right'):
        """
        Invert intervals.

        para data: 'right' use right side data, 'left' use left side data,
                   'none' for no data
        """
        ret = IvTree2()
        last_end = float('-inf')
        assert use_data in ['left', 'right', 'none']
        last_data = None
        for iv in sorted(self):
            if use_data == 'left':
                data = last_data
                last_data = iv.data
            elif use_data == 'right':
                data = iv.data
            else:  # use_data == 'none'
                data = None
            ret.addi(last_end, iv.begin, data)
            last_end = iv.end
        ret.addi(last_end, float('inf'), last_data)
        return ret

    def __invert__(self):
        """Invert intervals."""
        return self.notx(use_data='right')

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
            elif isinstance(other, IntervalTree):
                o_begin = other.begin()
                o_end = other.end()
            ret = IvTree2(self.overlap(o_begin, o_end))
            ret._chops(~other)
        return ret

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
