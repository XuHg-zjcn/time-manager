from datetime import datetime, timedelta
from enum import Enum
import re
import sys
sys.path.append("..")
import smart_strptime as sspt

re_c = re.compile('^(n(ow)?)?([+-])?')


class OutType(Enum):
    datetime = 0
    timestamp = 1
    string = 2

class Time_input:
    def __init__(self, output_type=OutType.datetime, init_value=None):
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
            value = self._convert_output_type(value)
        except Exception as e:
            print(e)
            return None
        else:
            return value

    def _convert_output_type(self, datetime_obj):
        if self.output_type == OutType.datetime:
            return datetime_obj
        elif self.output_type == OutType.timestamp:
            return datetime_obj.timestamp()
        elif self.output_type == OutType.string:
            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    def _process(self, in_str):
        self.in_str = in_str
        now, char = self._now_char()
        if now is True:                  # now[+-]* n
            self.last_value = datetime.now()
        elif char is None:               # datetime
            self.last_value = self._get_datetime()
        else:                            # last[+-]*
            pass
        self.last_value += self._puls_sub_char(char)
        return self.last_value

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

    def _puls_sub_char(self, char):
        ret = {None:0, '+':1, '-':-1}[char]
        if ret != 0:
            ret *= self._get_timedelta()
        else:
            ret = timedelta(0)
        return ret

    def _get_timedelta(self):
        tdstr = sspt.TimeDelta_str(self.in_str)
        tdstr.process_check()
        return tdstr.as_timedelta()

    def _get_datetime(self):
        dtstr = sspt.DateTime_str(self.in_str)
        dtstr.process_check()
        dt_obj = dtstr.as_datetime()
        return dt_obj

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
                value = self._convert_output_type(value)
            except Exception as e:
                print(e)
                info = '请重新输入:'
                continue      # error happend
            else:
                return value  # OK
