# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import pandas as pd

from Qt_GUI.pandasModel import ColumnSet, TableColumnSpinBox, ShowStat
from my_libs.ivtree2 import IvTree2
from my_libs.smart_strptime.MTshort import MTshort
from commd_line.init_config import conf, conn
from my_libs.argb import ARGB
from my_libs.sqltable import SqlTable

mts1 = MTshort('? Y-? m-? d % H:%0M:%0S')
mts2 = MTshort('? m-? d % H:%0M:%0S')


class Plan(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_default('rec_id', -1)
        self.apply_default('type_id', -1)
        self.apply_default('name', 'untitled')
        self.apply_default('num', 0)
        assert 'sta' in self
        assert 'end' in self
        self.apply_default('use', self['end'] - self['sta'])
        assert self['use'] >= 0
        self.apply_default('state', 0)

    def apply_default(self, key, value):
        if key not in self:
            self[key] = value

    def __str__(self):
        #            id   type  name   sta     end   state
        ret_fmt = '{:>6}|{:>4}|{:<25}| {:>19} | {:^14} |{}'
        sta_str = mts1.strftime(datetime.fromtimestamp(self['sta']))
        end_str = mts2.strftime(datetime.fromtimestamp(self['end']))
        ret_str = ret_fmt.format(self['id'], self['type_id'], self['name'],
                                 sta_str, end_str, self['state'])
        return ret_str

    def __repr__(self):
        sta_dt = datetime.fromtimestamp(self['sta'])
        end_dt = datetime.fromtimestamp(self['end'])

        ret = 'id={}, type={}, name={}\n'\
              .format(self['id'], self['type_id'], self['name'])
        ret += 'sta_time:{}\n'.format(sta_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'end_time:{}\n'.format(end_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'state:{}'.format(self['state'])
        return ret

    def get_collect_color(self, colls, default=0xffffff00,):
        argb = colls.get_conds_onlyone({'id': self['rec_id']},
                                       'color', default)
        return ARGB.from_argb(argb)

    def __getitem__(self, item):
        if item in self:
            return super().__getitem__(item)
        else:
            # used for format, don't use `None`, else raise TypeError below:
            # TypeError: unsupported format string passed to NoneType.__format__
            return 'None'


class Plans(pd.DataFrame):
    str_head = '   id | typ| name{}|{}start time{}|{}end time{}|stat\n'\
           .format(*(' '*i for i in [20, 6, 5, 4, 3]))

    @staticmethod
    def p_part(parts):
        ret = ''
        for p_ser in parts.iloc:
            ret += str(Plan(**p_ser)) + '\n'
        return ret

    def __repr__(self):
        ret = ''
        ret += Plans.str_head
        if len(self) <= int(conf['show']['print_max']):
            ret += self.p_part(self[0:])
        else:
            side = int(conf['show']['print_side'])
            ret += self.p_part(self[:side])
            N_skips = len(self) - 2*side
            ret += '{:-^80}\n'.format(' {} skips '.format(N_skips))
            ret += self.p_part(self[-side:])
        ret += '{:-^80}\n'.format('{} plans found'.format(len(self)))
        return ret

    def __str__(self):
        if len(self) == 0:
            return ''
        else:
            return self.__repr__()

    def get_ivtree(self, data_func):
        """
        para data_func: a func get plan, return will be ivtree data
        example:
            lambda p:p        # plan as ivtree data, used in GUI
            lambda p:p.color  # color of plan as ivtree data, used in CLI
        """
        ivtree = IvTree2()
        for plan in self.iloc:
            sta = float(plan['sta'])
            end = float(plan['end'])
            if sta < end:
                ivtree[sta:end] = data_func(plan)
        return ivtree

    def str_datetime(self):
        if len(self) == 0:
            return self
        df2 = self.copy()
        # TODO: use system local time, tz_convert('Asia/Shanghai') failed
        df2['sta'] = pd.to_datetime(df2['sta'], unit='s')
        df2['end'] = pd.to_datetime(df2['end'], unit='s')
        return df2


class ColumnSetTasks(ColumnSet):
    def __init__(self, name):
        super().__init__(name)
        self['num'] = TableColumnSpinBox(ShowStat.Yes, 100)


class TaskTable(SqlTable):
    name2dtype = [('rec_id', 'INT'),
                  ('type_id', 'INT'),
                  ('name', 'TEXT'),
                  ('num', 'NUMERIC'),
                  ('sta', 'REAL'),
                  ('end', 'REAL'),
                  ('use', 'REAL'),
                  ('state', 'INT')]
    table_name = 'tasks'

    def get_conds_plans(self, cond_dict):
        df = self.get_conds_dataframe(cond_dict)
        return Plans(df)

    def print_doings(self):
        plans = self.get_conds_plans({'state': 1})
        print('{} plans doing'.format(len(plans)))
        print('')

    def print_need(self):
        now = time.time()
        need_start = self.get_conds_plans({'state': 0, 'sta': ('<=', now)})
        need_stop = self.get_conds_plans({'state': 1, 'end': ('<=', now)})
        print('need start:')
        print(need_start)
        print('need stop:')
        print(need_stop)


tdb = TaskTable(conn)
task_tab = TaskTable(conn)
