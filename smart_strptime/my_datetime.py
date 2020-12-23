"""
Created on Mon Dec  7 15:56:59 2020

@author: xrj
some code copy from datetime module
"""
from numbers import Number
from datetime import date, datetime, timedelta
from time import struct_time
from .datetime_str import DateTime_str
from my_libs.ivtree2.iv2 import Iv2


class sTimeDelta(timedelta):
    def __new__(cls, days=0, seconds=0, microseconds=0, months=0,
                milliseconds=0, minutes=0, hours=0, weeks=0, years=0, **kwargs):
        months += years*12
        if isinstance(days, sTimeDelta):
            return days
        elif isinstance(days, timedelta):  # allow use timedelta
            seconds = days.seconds
            microseconds = days.microseconds
            days = days.days
        self = super().__new__(cls, days, seconds, microseconds,
                               milliseconds, minutes, hours, weeks, **kwargs)
        self._months = months
        return self

    @property
    def months(self):
        return self._months

    def __add__(self, other):
        if isinstance(other, timedelta):
            _months = self._months
            if hasattr(other, '_months'):
                _months += other._months
            return sTimeDelta(super().__add__(other), months = _months)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, timedelta):
            _months = self._months
            if hasattr(other, '_months'):
                _months -= other._months
            return sTimeDelta(super().__sub__(other), months = _months)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, timedelta):
            return -self + other
        return NotImplemented

    def __neg__(self):
        return sTimeDelta(-self.days,
                          -self.seconds,
                          -self.microseconds,
                          -self._months)

    def __pos__(self):
        return self

    def __abs__(self):
        if self._months < 0 or (self.days < 0 and self._months == 0):
            return -self
        else:
            return self

    def __mul__(self, other):
        if isinstance(other, int):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            return sTimeDelta(super().__mul__(other),
                              months=self._months*other)
        if isinstance(other, float):
            if self._months != 0:
                raise ValueError("sTimeDelta with months can't multipy float")
            return sTimeDelta(super().__mul__(other))
        return NotImplemented

    __rmul__ = __mul__

    def _no_months(self, func):
        if self._months == 0:
            return func(super())
        else:
            raise ValueError("delta months must 0")

    def __floordiv__(self, other):
        return self._no_months(lambda x: x.__floordiv__(other))

    def __truediv__(self, other):
        return self._no_months(lambda x: x.__truediv__(other))

    def __mod__(self, other):
        return self._no_months(lambda x: x.__mod__(other))

    def __divmod__(self, other):
        return self._no_months(lambda x: x.__divmod__(other))

    def _getstate(self):
        return (self.days, self.seconds, self.microseconds, self._months)

    def as_timedelta(self, day_per_month):
        days = self.days + self._months*day_per_month
        return timedelta(days, self.seconds, self.microseconds)

    def __eq__(self, other):
        if isinstance(other, Number) and other == 0:
            return not any(self._getstate())
        else:
            return self._getstate() == other._getstate()

    def _cmp(self, other):
        lmin = self.as_timedelta(28)
        lmax = self.as_timedelta(31)
        if isinstance(other, sTimeDelta):
            rmin = other.as_timedelta(28)
            rmax = other.as_timedelta(31)
        elif isinstance(other, timedelta):
            rmin = rmax = other
        else:
            raise TypeError("unsupport type '{}' compare with sTimeDelta"
                            .format(type(other)))
        if lmax < rmin:
            value = 1
        elif rmax < lmin:
            value = -1
        else:
            value = 0
        return value

    def _cmp0(self, other):
        """
        allow compare with 0
        """
        if isinstance(other, Number):
            if other == 0:
                return self._cmp(timedelta(0))
            else:
                raise ValueError('sTimeDelta compare with number not zero')
        else:
            return self._cmp(other)

    def __le__(self, other):
        return self._cmp0(other) <= 0

    def __lt__(self, other):
        return self._cmp0(other) < 0

    def __ge__(self, other):
        return self._cmp0(other) >= 0

    def __gt__(self, other):
        return self._cmp0(other) > 0

    def __repr__(self):
        args = []
        if self._months:
            args.append("months=%d" % self._months)
        if self.days:
            args.append("days=%d" % self.days)
        if self.seconds:
            args.append("seconds=%d" % self.seconds)
        if self.microseconds:
            args.append("microseconds=%d" % self.microseconds)
        if not args:
            args.append('0')
        return "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ', '.join(args))

    def __str__(self):
        ret = super().__str__()
        if self._months:
            def plural(n):
                return n, abs(n) != 1 and "s" or ""
            ret = '%d month%s, ' % plural(self._months) + ret
        return ret


class sDateTime(datetime):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, Number):
                if 0 <= arg <= 9999:
                    # raise Error, required month and day
                    return super().__new__(cls, arg)
                elif arg < 5e8 or arg > 5e9:
                    print("Waring: timestamp {} mean {}, "
                          "maybe isn't a unix timestamp"
                          .format(arg, datetime.fromtimestamp(arg)))
                return super().fromtimestamp(arg)
            elif isinstance(arg, datetime):
                return super().__new__(cls, arg.year, arg.month, arg.day,
                                       arg.hour, arg.minute, arg.second,
                                       arg.microsecond)
            elif isinstance(arg, struct_time):  # not suggest use
                return super().__new__(cls, arg.tm_year, arg.tm_mon, arg.tm_mday,
                                       arg.tm_hour, arg.tm_min, arg.tm_sec)
            elif isinstance(arg, str):
                dati_str = DateTime_str(arg)
                dati_str.process_check()
                self = dati_str.as_datetime()
                return self
            else:
                raise TypeError("unsupported type '{}' convert to sDaTi"
                                .format(type(arg)))
        else:
            return super().__new__(cls, *args, **kwargs)

    def _op_with_months(self, other, func):
        if isinstance(other, timedelta):
            tmp = func(super(), other)
            if hasattr(other, 'months') and other.months != 0:
                mon = func(tmp.month, other.months)
                y_, mon = divmod(mon-1, 12)
                d = date(tmp.year+y_, mon+1, tmp.day)
                return sDateTime.combine(d, tmp.time())
            else:
                return tmp
        return NotImplemented

    def __add__(self, other):
        return self._op_with_months(other, lambda x, y: x.__add__(y))

    def __sub__(self, other):
        return self._op_with_months(other, lambda x, y: x.__sub__(y))

    def __int__(self):
        return int(self.timestamp())

    def __float__(self):
        return self.timestamp()


class sTimeRange:
    @classmethod
    def isOKType(cls, x):
        return x is None or isinstance(x, datetime)

    def __new__(cls, begin, end):
        if cls.isOKType(begin) and cls.isOKType(end):
            pass
        elif isinstance(begin, timedelta) and isinstance(end, timedelta):
            end = begin + end
        elif isinstance(begin, timedelta) and isinstance(end, datetime):
            begin = end + begin
        else:
            raise TypeError('unsupported sTimeRange combine')
        self = object.__new__(cls)
        self._begin = begin
        self._end = end
        self._check_cmp()
        return self

    @property
    def begin(self):
        return self._begin

    @property
    def end(self):
        return self._end

    def _check_cmp(self, isRaise=True, notNone=False):
        if all((self._begin, self._end)):
            ret = self._begin <= self._end  # True OK
        else:
            ret = None
        if isRaise:
            if ret is False:
                raise ValueError('begin{} after end{}'
                                 .format(self._begin, self._end))
            elif notNone and ret is None:
                raise ValueError('not allow None here')
        return ret

    @classmethod
    def M(cls, year, month=None, day=None, hour=None, minute=None, second=None):
        paras = [year, month, day, hour, minute, second, None]
        name_paras = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
        maxi = paras.index(None)
        name = name_paras[maxi-1]
        if maxi < 6 and len(set(paras[maxi:])) > 1:  # not same
            raise ValueError('rangeM can only continuous None in end')
        paras_begin = paras[:maxi]
        while len(paras_begin) < 3:
            paras_begin.append(1)
        begin = sDateTime(*paras_begin)
        d1 = sTimeDelta(**{name: 1})
        return cls(begin, begin+d1)

    def get_iv(self, data=None):
        return Iv2(float(self._begin), float(self._end), data)

    def __repr__(self):
        return "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ", ".join(map(repr, [self._begin, self._end])))

    def __str__(self):
        return "sTimeRange:\n{}\n{}".format(str(self._begin), str(self._end))

    def datetime_tuple(self):
        self._check_cmp()
        return (self._begin, self._end)

    def timestamp_tuple(self):
        self._check_cmp()
        return (self._begin.timestamp(), self._end.timestamp())

    def length(self):
        return self._end - self._begin
