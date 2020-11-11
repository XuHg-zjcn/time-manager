import time
import re
import sys
sys.path.append("..")
import smart_strptime as sspt

re_c = re.compile('^(n(ow)?)?([+-])?')


class Time_input:
    def __init__(self):
        self.last_value = None

    def print_help(self):
        print('''\
时间输入法:
n(ow):当前时间
n+,n-:与当前时间加减
+,-  :与上次输入的时间加减
无前置符号:输入完整时间
h:帮助, e:退出
''')

    def input_str(self, in_str):
        """Input str and return timestamp."""
        while True:
            if in_str in {'help', 'h'}:
                self.print_help()
                in_str = input('请重新输入:')
                continue
            if in_str in {'e', 'exit'}:
                return None
            if in_str.upper() in {'NONE', 'NULL'}:
                return None
            try:
                value = self._process(in_str)
            except Exception as e:
                print('Error:', e)
                in_str = input('请重新输入, h:帮助, e:退出:')
                if in_str in {'e', 'exit'}:
                    return None
                continue
            else:
                return value

    def _process(self, in_str):
        self.in_str = in_str
        now, char = self._now_char()
        if now is True:            # now[+/-]  n+ n-, n
            value = time.time()
            value = self._puls_sub_char(char, value)
        elif char is not None:     # (last)[+/-]  + -
            if self.last_value is None:
                raise ValueError('use last value in first input')
            value = self.last_value
            value = self._puls_sub_char(char, value)
        else:                      # re not match
            value = self._get_datetime()
        assert 1e9 < value < 2.5e9  # check value year 2001<x<2049
        self.last_value = value
        return value

    def _now_char(self):
        match = re_c.match(self.in_str)
        if match is not None:
            self.in_str = self.in_str[match.span(0)[1]:]
            now = match.group(1) is not None
            puls_sub = match.group(3)
            if now and puls_sub is None and len(self.in_str) != 0:
                raise ValueError('now without puls or sub, must no more str!')
        else:
            now = False
            puls_sub = None
        return now, puls_sub

    def _puls_sub_char(self, char, value):
        if char is None:
            return value
        elif char == '+':
            return value + self._get_timedelta()
        elif char == '-':
            return value - self._get_timedelta()

    def _get_timedelta(self):
        tdstr = sspt.TimeDelta_str(self.in_str)
        tdstr.process_check()
        return tdstr.as_sec()

    def _get_datetime(self):
        dtstr = sspt.DateTime_str(self.in_str)
        dtstr.process_check()
        dt_obj = dtstr.as_datetime()
        return dt_obj.timestamp()
