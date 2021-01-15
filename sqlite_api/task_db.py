# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd

from my_libs.ivtree2 import IvTree2
from smart_strptime.MTshort import MTshort
from commd_line.init_config import init_config
from .argb import ARGB
from .sqltable import SqlTable

conf = init_config()
mts1 = MTshort('? Y-? m-? d % H:%0M:%0S')
mts2 = MTshort('? m-? d % H:%0M:%0S')


class Plan(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_defalut('rec_id', -1)
        self.apply_defalut('type_id', -1)
        self.apply_defalut('name', 'untitled')
        self.apply_defalut('num', 0)
        assert 'sta' in self
        assert 'end' in self
        self.apply_defalut('use', self['end']-self['sta'])
        assert self['use'] >= 0
        self.apply_defalut('state', 2)

    def apply_defalut(self, key, value):
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

    def get_collect_color(self, colls, default=0xffffff00):
        argb = colls.get_conds_onlyone({'id':self['rec_id']}, ['color'], default)
        return ARGB.from_argb(argb)


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

    __str__ = __repr__

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


class TaskTable(SqlTable):
    name2dtype = [('rec_id', 'INT'), ('type_id', 'INT'), ('name', 'TEXT'), ('num', 'NUMERIC'),
                  ('sta', 'REAL'), ('end', 'REAL'), ('use', 'REAL'), ('state', 'INT')]
    table_name = 'tasks'

    def add_aitem(self, plan, commit=None):
        self.insert(plan, commit)

    def get_conds_plans(self, cond_dict):
        df = self.get_conds_dataframe(cond_dict)
        return Plans(df)

    def print_doings(self):
        plans = self.get_conds_plans({'state': 1})
        print('{} plans doing'.format(len(plans)))
        if len(plans) != 0:
            print(plans)
        else:
            print('')
