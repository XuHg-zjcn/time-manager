from datetime import datetime
from enum import Enum
import time
import re
import sys
sys.path.append("..")
import smart_strptime as sspt

re_c = re.compile('^(n(ow)?)?([+-])?')


class OutType(Enum):
    sec = 0
    datetime = 1
    string = 2

class Time_input:
    def __init__(self, output_type=OutType.sec, init_value=None):
        """
        :output_type: 'sec' or 'datetime'.
        :init_value: the init value, if None first input can't use relative time.
        """
        self.output_type = output_type
        self.last_value = init_value

    def __call__(self, in_str):
        """Input str and return output."""
        try:
            value = self._process(in_str)
        except Exception as e:
            print(e)
            return None
        else:
            return value

    def _process(self, in_str):
        self.in_str = in_str
        now, char = self._now_char()
        if now is True:            # now[+/-]  n+ n-, n
            if self.output_type is OutType.sec:
                value = time.time()
            elif self.output_type is OutType.datetime:
                value = datetime.now()
            value = self._puls_sub_char(char, value)
        elif char is not None:     # (last)[+/-]  + -
            if self.last_value is None:
                raise ValueError('use last value in first input')
            value = self.last_value
            value = self._puls_sub_char(char, value)
        else:                      # re not match
            value = self._get_datetime()
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
        if self.output_type is OutType.sec:
            return time.time()
        elif self.output_type is OutType.datetime:
            return datetime.now()

    def _get_datetime(self):
        dtstr = sspt.DateTime_str(self.in_str)
        dtstr.process_check()
        dt_obj = dtstr.as_datetime()
        return dt_obj.timestamp()

class CLI_Inputer(Time_input):
    def print_help(self):
        print('时间输入法:\n'
              'n(ow):当前时间\n'
              'n+,n-:与当前时间加减\n'
              '+,-  :与上次输入的时间加减\n'
              '无前置符号:输入完整时间\n'
              'h:帮助, e:退出\n')
    def __call__(self, info):
        """Input str and return timestamp."""
        while True:
            in_str = input(info)
            # input controls
            if in_str.upper() in {'HELP', 'H'}:
                self.print_help()
                info = '请重新输入:'
                continue      # after print help
            if in_str.upper() in {'E', 'EXIT', 'NONE', 'NULL'}:
                return None   # exit
            # process
            try:
                value = self._process(in_str)
            except Exception as e:
                print(e)
                info = '请重新输入:'
                continue      # error happend
            else:
                return value  # OK
