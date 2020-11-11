import sqlite3
import os
import time
import datetime
import numpy as np


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
        if sta_time > end_time:
            raise ValueError('start time later than end time')
        if use_time < 0:
            raise ValueError('use time < 0')
        if sub_time < 0:
            raise ValueError('sub time < 0')
        length = end_time - sta_time
        use_sub = use_time + sub_time
        if use_sub > length:
            raise ValueError('use + sub > time range length')
        self.sta_time = sta_time
        self.end_time = end_time
        self.use_time = use_time
        self.sub_time = sub_time

    def db_nums(self):
        return self.sta_time, self.end_time, self.use_time, self.sub_time


class Plan:
    def __init__(self, dbtype: int, name: str, p_time,
                 tree_i=None, finish=False, dbid=None):
        self.dbtype = dbtype
        self.name = name
        if tree_i is None:
            tree_i = TreeItem()
        self.tree_i = tree_i
        self.p_time = p_time
        self.dbid = dbid
        self.finish = finish

    def db_item(self):
        ret = [self.dbtype, self.name]
        ret += self.tree_i.db_BLOBs()
        ret += self.p_time.db_nums()
        ret.append(self.finish)
        return ret

    def __str__(self):
        dt_obj = datetime.datetime.fromtimestamp(self.p_time.sta)
        sta_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
        dt_obj = datetime.datetime.fromtimestamp(self.p_time.end)
        end_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
        use_str = datetime.timedelta(seconds=self.p_time.use)
        use_str = str(use_str)
        sub_str = datetime.timedelta(seconds=self.p_time.sub)
        sub_str = str(sub_str)
        return 'name:{}, start:{}, end:{}, use:{}, sub:{}'\
               .format(self.name, sta_str, end_str, use_str, sub_str)

class TODO_db:
    def __init__(self, db_path='TODO.db'):
        self.db_path = db_path
        if not os.path.exists(db_path):
            self.db_init()
        else:
            self.conn = sqlite3.connect(self.db_path)

    def db_init(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        sql = '''CREATE TABLE todo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type     INT,   name     TEXT,
            pares    BLOB,  subs     BLOB,  reqs     BLOB,
            sta_time REAL,  end_time REAL,  use_time REAL,  sub_time REAL,
            finish   BOOL);'''
        self.c.execute(sql)
        self.conn.commit()

    def add_aitem(self, plan):
        self.c = self.conn.cursor()
        sql = "INSERT INTO todo VALUES(NULL,?,?,?,?,?,?,?,?,?,?);"
        self.c.execute(sql, plan.db_item())
        self.conn.commit()

    def get_aitem(self, cond_dict):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        sql = 'SELECT * FROM todo WHERE '
        paras = []
        allow_filed = {'id', 'type', 'name', 'sta_time', 'end_time',
                       'use_time', 'sub_time', 'finish'}
        assert len(cond_dict) > 0
        for key in cond_dict.keys():
            assert key in allow_filed
            value = cond_dict[key]
            if value is None:
                continue
            elif type(value) in [bool, int, float]:               # x == ?
                sql += '{}=? and'.format(key)
                paras.append(value)
            elif isinstance(value, tuple) and len(value) == 2:  # a <= x < b
                if type(value[0]) in [int, float]:
                    sql += '?<={0} and {0}<? and'.format(key)
                    paras.append(value[0])
                    paras.append(value[1])
                elif value[0] in ['<', '>']:
                    sql += '{}{} and'.format(key, value[0])
                else:
                    raise ValueError('tuple invaild')
            else:
                raise ValueError('key type invaild')
        sql = sql[:-4]
        res = self.c.execute(sql, paras)
        # assert len(res) == 13
        # return Plan(*res[:3], TreeItem(*res[3:5]), PlanTime(*res[5:]))
        return res


# test code
if __name__ == '__main__':
    tdb = TODO_db()
    tdb.add_aitem(Plan(1, 'plan1', TreeItem(0), PlanTime('n', ('n', 10), 5)))
    tdb.get_aitem({'sta_time': (1604489926.0, 1604489926.9)})
