import sqlite3
import os
import time
from datetime import datetime
import numpy as np
from my_libs.ivtree2 import IvTree2
from smart_strptime.MTshort import MTshort
from commd_line.init_config import init_config
from .argb import ARGB

conf = init_config()
mts = MTshort()


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
                 tree_i=None, finish=False, dbid=None, color=None, db=None):
        """
        p_time can from sqlite SELECT * tuple
        p_time defalut is current time
        """
        if p_time is None:
            p_time = PlanTime.now()
        if isinstance(p_time, tuple):
            assert len(p_time) == 13
            dbid = p_time[0]
            dbtype = p_time[1]
            name = p_time[2]
            finish = p_time[11]
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
        self.finish = finish
        self.color_flag = color is not None
        if self.color_flag:
            self.color = color
        elif db is not None:
            dbt = db.find_dbtype(dbtype)
            self.color = dbt.color if dbt is not None else None
        else:
            self.color = None

    def db_item(self):
        ret = [self.dbtype, self.name, self.num]
        ret += self.tree_i.db_BLOBs()
        ret += self.p_time.db_nums()
        ret.append(self.finish)
        ret.append(self.color.ARGBi() if self.color is not None else None)
        return ret

    def __str__(self):
        #            id   type  name   sta     end   finish
        ret_fmt = '{:>4}|{:>3}|{:<16}|{:>19} ~{:>14}|{:<6}'
        sta_str = mts.strftime(datetime.fromtimestamp(self.p_time.sta), update=True)
        end_str = mts.strftime(datetime.fromtimestamp(self.p_time.end), update=False)
        dbid = self.dbid if self.dbid is not None else 0
        ret_str = ret_fmt.format(dbid, self.dbtype, self.name,
                                 sta_str, end_str, self.finish)
        return ret_str

    def __repr__(self):
        sta_dt = datetime.fromtimestamp(self.p_time.sta)
        end_dt = datetime.fromtimestamp(self.p_time.end)

        ret = 'id={}, type={}, name={}\n'\
              .format(self.dbid, self.dbtype, self.name)
        ret += 'sta_time:{}\n'.format(sta_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'end_time:{}\n'.format(end_dt.strftime('%Y/%m/%d.%H:%M:%S'))
        ret += 'finish:{}'.format(self.finish)
        return ret


class Plans(list):
    str_head = ' id |typ|name{}|{}start time{}~{}end time{}|finish\n'\
           .format(*(' '*i for i in [12, 5, 5, 6, 5]))

    def __init__(self, iterable, db):  # sqlite3.Cursor
        super().__init__()
        for tup in iterable:
            self.append(Plan(tup, db=db))

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
            ret += '{:-^68}\n'.format(' {} skips '.format(N_skips))
            for plan in self[-side:]:
                ret += str(plan) + '\n'
        if len(self) >= int(conf['show']['print_max']):
            ret += '{:-^68}\n'.format('{} plans found'.format(len(self)))
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


class TaskDB:
    def __init__(self, db_path, table_name, commit_each=False):
        self.table_name = table_name
        self.db_path = db_path
        self.commit_each = commit_each
        if not os.path.exists(db_path):
            self.create_table()
        else:
            self.conn = sqlite3.connect(self.db_path)
            cur = self.conn.cursor()
            sql = 'SELECT name FROM sqlite_sequence;'
            table_exists = cur.execute(sql)
            if (self.table_name,) not in table_exists:
                self.create_table()

    def create_table(self):
        self.conn = sqlite3.connect(self.db_path)
        cur = self.conn.cursor()
        sql = '''CREATE TABLE {}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type     INT,   name     TEXT,  num      NUMERIC,
            pares    BLOB,  subs     BLOB,  reqs     BLOB,
            sta_time REAL,  end_time REAL,  use_time REAL,  sub_time REAL,
            finish   BOOL,  color);'''.format(self.table_name)
        cur.execute(sql)
        self.add_aitem(Plan(None, -1, 'root'))  # add root item
        self.conn.commit()

    def add_aitem(self, plan):
        cur = self.conn.cursor()
        sql = 'INSERT INTO {}(type, name, num, pares, subs, reqs, '\
              'sta_time, end_time, use_time, sub_time, finish, color)'\
              'VALUES(?,?,?,?,?,?,?,?,?,?,?,?);'.format(self.table_name)
        cur.execute(sql, plan.db_item())
        if self.commit_each:
            self.conn.commit()

    def commit(self):
        if self.commit_each:
            raise RuntimeWarning('commit each change is Enable')
        self.conn.commit()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def close(self):
        self.conn.close()

    def get_plans_cond(self, cond_dict):
        """
        Get Plans matched conditions.
        :para cond_dict: {'field1':value, 'field2':(min, max), 'field3':('<', value), ...}
        """
        cur = self.conn.cursor()
        sql = 'SELECT * FROM {} WHERE '.format(self.table_name)
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
        sql = sql[:-5] # remove end of str ' and '
        res = cur.execute(sql, paras)
        return Plans(res, self)

    def find_dbtype(self, dbtype):
        plans = self.get_plans_cond({'type':1, 'num':dbtype})
        if len(plans) == 0:
            return None
        elif len(plans) == 1:
            return plans[0]
        else:
            raise ValueError('find more than one dbtype'.format(dbtype))
