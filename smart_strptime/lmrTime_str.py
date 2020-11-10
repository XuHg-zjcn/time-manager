"""
Created on Tue Nov 10 12:49:54 2020

@author: xrj
"""
import re
from smart_strptime.my_str import Part, BigPart, My_str, sType
from smart_strptime.basetime import UType, UxType

re_lmrs = re.compile(r'(\d+):(\d+:)?(\d+)(\.\d+)?')
ampm = ['AM', 'PM']


class lmrTime_str(My_str):
    def __init__(self, in_str):
        super().__init__(in_str)
        self.time_p = BigPart(self, 'time', UxType['lmrTime'])

    def process(self):
        self.__time_lmrs()
        self.__get_AMPM()

    def __time_lmrs(self):
        """Get time LL:MM:RR.subsec.

        Middle and Subsec can skip.
        """
        m, sp = self.search(re_lmrs)
        if sp is None:
            return
        self.flags.add('time_found')
        # append Parts to self.time_parts
        self.time_p[UType.left] = Part(self, sp[1], sType.num)
        self.time_p[sType.norm] = \
            Part(self, (sp[1].e, sp[1].e+1), sType.norm)
        # middle item found
        if m.group(2) is not None:
            self.time_p[UType.midd] = \
                Part(self, (sp[2].s, sp[2].e-1), sType.num)
            self.time_p[sType.norm] = \
                Part(self, (sp[2].e-1, sp[2].e), sType.norm)

        self.time_p[UType.right] = Part(self, sp[3], sType.num)
        # subsec found
        if m.group(4) is not None:
            self.time_p[UType.subsec] = Part(self, sp[4], sType.num)

    def set_time_p(self, n2v=None):
        """Set time lmrs to hmss.

        ll:mm:rr        -> HH:MM:SS
        ll:mm:rr.sss... -> HH:MM:SS.subsec
              rr.sss... ->       SS.subsec
        ll :  rr.sss... ->    MM:SS.subsec
        ll :  rr          ?-> HH:MM or MM:SS
        @para n2v: if found ll:rr, such as 12:34,
                   'hour' for HH:MM, 'second' for MM:SS, None raise ValueError
        """
        assert 'set_time_p' not in self.flags  # no entry before
        B = UType
        #            src_keys              dst_keys
        dict_rule = {(B.lt, B.md, B.rt      ): (B.h, B.m, B.s      ),
                     (B.lt, B.md, B.rt, B.ss): (B.h, B.m, B.s, None),
                     (            B.rt, B.ss): (          B.s, None),
                     (B.lt,       B.rt, B.ss): (     B.m, B.s, None)}

        def get_src_keys(time_p):
            src_keys = []
            for key in (B.lt, B.md, B.rt, B.ss):
                if key in time_p:
                    src_keys.append(key)
            src_keys = tuple(src_keys)
            return src_keys

        def get_dst_keys(src_keys, dict_rule, n2v):
            # use dict_rule
            if src_keys in dict_rule:
                dst_keys = dict_rule[src_keys]
            # use n2v
            elif src_keys == (B.lt, B.rt):
                if n2v == 'hour':
                    dst_keys = (B.h, B.m)
                elif n2v == 'second':
                    dst_keys = (B.m, B.s)
                else:
                    raise ValueError('n2v must be hour or second')
            # empty src_keys
            elif src_keys == ():
                dst_keys = ()
            else:
                raise KeyError('src_keys {} not match'.format(src_keys))
            return dst_keys

        src_keys = get_src_keys(self.time_p)
        dst_keys = get_dst_keys(src_keys, dict_rule, n2v)
        assert len(src_keys) == len(dst_keys)
        for s_k, d_k in zip(src_keys, dst_keys):
            if d_k is not None:
                self.time_p[d_k] = self.time_p.pop(s_k)  # pop lmr to hms
        self.flags.add('set_time_p')

    def __get_AMPM(self):
        apm = self._find_strs(ampm, 'AMPM')
        if apm is not None:
            self.time_p[UType.ampm] = apm
