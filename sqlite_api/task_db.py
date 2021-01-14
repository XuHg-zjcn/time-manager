# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import pandas as pd
import numpy as np

from my_libs.ivtree2 import IvTree2
from smart_strptime.MTshort import MTshort
from commd_line.init_config import init_config
from .argb import ARGB

conf = init_config()
mts1 = MTshort('? Y-? m-? d % H:%0M:%0S')
mts2 = MTshort('? m-? d % H:%0M:%0S')


class TreeItem:
    """Plan tree node."""

    def __init__(self, pares=None, subs=None, reqs=None):
        def process(x):
            """Convert x to numpy array."""
            if x is None:
                return np.array([], np.uint64)
            if isinstance(x, int):
                x = [x]
            if isinstance(x, list):
                return np.array(x)
            elif isinstance(x, bytes):
                return np.frombuffer(x, np.uint64)
            else:
                raise TypeError('input type must int, list or bytes')
        self.pares = process(pares)
        self.subs = process(subs)
        self.reqs = process(reqs)

    def db_BLOBs(self):
        """Get sqlite db BLOB."""
        datas = [self.pares, self.subs, self.reqs]
        return tuple(map(lambda x: x.tostring(), datas))


class PlanTime:
    def __init__(self, sta_time, end_time, use_time=0, sub_time=0):
        if all([sta_time, end_time]) and sta_time > end_time:
            raise ValueError('start time later than end time')
        if use_time and use_time < 0:
            raise ValueError('use time < 0')
        if sub_time and sub_time < 0:
            raise ValueError('sub time < 0')
        length = end_time - sta_time if all([end_time, sta_time]) else None
        use_sub = use_time + sub_time if all([use_time, sub_time]) else None
        if all([use_sub, length]) and use_sub > length:
            raise ValueError('use + sub > time range length')
        self.sta = sta_time
        self.end = end_time
        self.use = use_time
        self.sub = sub_time

    def db_nums(self):
        return self.sta, self.end, self.use, self.sub

    @classmethod
    def now(cls):
        t = time.time()
        return cls(t, t)


class Plan:
    def __init__(self, p_time=None, dbtype=0, name='untitled', num=0,
                 tree_i=None, state=0, dbid=None, color=None, db=None):
        """
        p_time can from sqlite SELECT * tuple
        p_time defalut is current time

        :para state: 0 will do, 1 doing, 2 finish
        """
        if p_time is None:
            p_time = PlanTime.now()
        if isinstance(p_time, tuple):
            assert len(p_time) == 13
            dbid = p_time[0]
            dbtype = p_time[1]
            name = p_time[2]
            state = p_time[11]
            color = p_time[12]
            p_time = PlanTime(*p_time[7:11])
        if type(color) in [int, str]:
            color = ARGB.from_argb(color)
        self.p_time = p_time
        self.dbtype = dbtype
        self.name = name
        self.num = num
        if tree_i is None:
            tree_i = TreeItem()
        self.tree_i = tree_i
        self.dbid = dbid
        self.state = state
        if color is not None:
            pass
        elif db is not None:
            dbt = db.find_dbtype(dbtype)
            color = dbt.color if dbt is not None else None
        self.color = color

    def db_item(self):
        ret = [self.dbtype, self.name, self.num]
        ret += self.tree_i.db_BLOBs()
        ret += self.p_time.db_nums()
        ret.append(self.state)
        ret.append(self.color.ARGBi() if self.color is not None else None)
        return ret

    def __str__(self):
        #            id   type  name   sta     end   state
        ret_fmt = '{:>6}|{:>4}|{:<25}| {:>19} | {:^14} |{}'
        sta_str = mts1.strftime(datetime.fromtimestamp(self.p_time.sta))
        end_str = mts2.strftime(datetime.fromtimestamp(self.p_time.end))
        dbid = self.dbid if self.dbid is not None else 0
        ret_str = ret_fmt.format(dbid, self.dbtype, self.name,
                                 sta_str, end_str, self.state)
        return ret_str

    def __repr__(self):
        sta_dt = datetime.fromtimestamp(self.p_time.sta)
        end_dt = datetime.fromtimestamp(self.p_time.end)

        ret = 'id={}, type={}, name={}\n'\
              .format(self.dbid, self.dbtype, self.name)
        ret += 'sta_time:{}\n'.format(sta_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'end_time:{}\n'.format(end_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'state:{}'.format(self.state)
        return ret


class Plans(list):
    str_head = '   id | typ| name{}|{}start time{}|{}end time{}|stat\n'\
           .format(*(' '*i for i in [20, 6, 5, 4, 3]))

    def __init__(self, iterable, db):  # sqlite3.Cursor
        super().__init__()
        for obj in iterable:
            if isinstance(obj, Plan):
                self.append(obj)
            else:
                self.append(Plan(obj, db=db))

    def __repr__(self):
        ret = ''
        ret += Plans.str_head
        if len(self) <= int(conf['show']['print_max']):
            for plan in self:
                ret += str(plan) + '\n'
        else:
            side = int(conf['show']['print_side'])
            for plan in self[:side]:
                ret += str(plan) + '\n'
            N_skips = len(self) - 2*side
            ret += '{:-^80}\n'.format(' {} skips '.format(N_skips))
            for plan in self[-side:]:
                ret += str(plan) + '\n'
        if len(self) >= int(conf['show']['print_max']):
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
        for plan in self:
            sta = plan.p_time.sta
            end = plan.p_time.end
            if sta < end:
                ivtree[sta:end] = data_func(plan)
        return ivtree


def optional_assign(obj, name, value=None):
    if value is not None:
        setattr(obj, name, value)
    elif hasattr(obj, name):
        pass
    else:
        raise ValueError("value is None and '{}' object has no attribute '{}'".format(type(obj), name))


class SqlTable:
    name2dtype = [('example_int', 'INT'), ('example_text', 'TEXT')]
    table_name = 'table_name'

    def __init__(self, conn, table_name=None, name2dtype=None, commit_each=False):
        """
        Examples
        --------
        table_name: 'tab'
        name2type_dict: [('name','TEXT'), ('num','REAL')]
        """
        self.conn = conn
        optional_assign(self, 'table_name', table_name)
        optional_assign(self, 'name2dtype', name2dtype)
        self.commit_each = commit_each
        self.create_table(commit=True)

    def create_table(self, commit=True):
        cur = self.conn.cursor()
        fields = []
        for name, dtype in self.name2dtype:
            if dtype:
                fields.append('{} {}'.format(name, dtype))
            else:
                fields.append(str(name))
        fields = ', '.join(fields)
        sql = 'CREATE TABLE IF NOT exists {}('\
              'id INTEGER PRIMARY KEY AUTOINCREMENT, {})'
        cur.execute(sql.format(self.table_name, fields))
        if commit or self.commit_each:
            self.conn.commit()

    def insert(self, values, commit=None):
        cur = self.conn.cursor()
        if not isinstance(values, dict):
            val_d = {}
            for v, (k, _) in zip(values, self.name2dtype):
                val_d[k] = v
        else:
            val_d = values
        sql = 'INSERT INTO {}({}) VALUES({})'
        sqf = sql.format(self.table_name,
                         ', '.join(val_d.keys()),
                         ('?,'*len(val_d))[:-1])
        cur.execute(sqf, list(val_d.values()))
        if commit or self.commit_each:
            self.conn.commit()

    def commit(self):
        if self.commit_each:
            raise RuntimeWarning('commit each change is Enable')
        self.conn.commit()

    def conds_sql(self, cond_dict, fields=None):
        """
        Get Plans matched conditions.
        :para cond_dict: {'field1':value, 'field2':(min, max), 'field3':('<', value), ...}
        """
        fields_str = ', '.join(fields) if fields else '*'
        sql = 'SELECT {} FROM {} WHERE '.format(fields_str, self.table_name)
        paras = []
        assert len(cond_dict) > 0
        for key in cond_dict.keys():
            value = cond_dict[key]
            if value is None:
                continue
            elif type(value) in [bool, int, float]:             # x == ?
                sql += '{}=? and '.format(key)
                paras.append(value)
            elif isinstance(value, tuple) and len(value) == 2:  # a <= x < b
                if type(value[0]) in [int, float]:
                    sql += '?<={0} and {0}<? and '.format(key)
                    paras += value
                elif value[0] in ['<', '>', '>=', '<=', '=', '==', '!=']:
                    sql += '{}{}? and '.format(key, value[0])
                    paras.append(value[1])
                else:
                    raise ValueError('tuple invaild')
            else:
                raise ValueError('key type invaild')
        sql = sql[:-5]  # remove end of str ' and '
        return sql, paras

    def get_conds_execute(self, cond_dict, fields=None):
        cur = self.conn.cursor()
        sql, paras = self.conds_sql(cond_dict, fields)
        return cur.execute(sql, paras)

    def get_conds_dataframe(self, cond_dict, fields=None):
        sql, paras = self.conds_sql(cond_dict, fields)
        return pd.read_sql_query(sql, self.conn, params=paras)


class TaskTable(SqlTable):
    name2dtype = [('type', 'INT'), ('name', 'TEXT'), ('num', 'NUMERIC'),
                  ('pares', 'BLOB'), ('subs', 'BLOB'), ('reqs', 'BLOB'),
                  ('sta_time', 'REAL'), ('end_time', 'REAL'), ('use_time', 'REAL'),
                  ('sub_time', 'REAL'), ('state', 'INT'), ('color', None)]

    table_name = 'tasks'

    def __init__(self, conn, commit_each=False):
        super().__init__(conn, self.table_name, self.name2dtype, commit_each)

    def add_aitem(self, plan, commit=None):
        self.insert(plan.db_item(), commit)

    def get_plans_cond(self, cond_dict):
        return Plans(self.get_conds_execute(cond_dict), self)

    def find_dbtype(self, dbtype):
        plans = Plans(self.get_plans_cond({'type': 1, 'num': dbtype}), self)
        if len(plans) == 0:
            return None
        elif len(plans) == 1:
            return plans[0]
        else:
            raise ValueError('find more than one dbtype'.format(dbtype))

    def print_doings(self):
        plans = self.get_plans_cond({'state': 1})
        print('{} plans doing'.format(len(plans)))
        if len(plans) != 0:
            print(plans)
        else:
            print('')
