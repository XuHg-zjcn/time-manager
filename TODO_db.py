import sqlite3
import os
import time
import datetime
import numpy as np

class TreeItem:
    def __init__(self, pares=[], subs=[]):
        if isinstance(pares, int):
            pares = [pares]
        if isinstance(subs, int):
            subs = [subs]
        #init by lists
        if isinstance(pares, list) and isinstance(subs, list):
            self.pares = np.array(pares)
            self.subs  = np.array(subs)
        #init by sqlite BLOB
        elif isinstance(pares, bytes) and isinstance(subs, bytes):
            assert len(pares)%8 == len(subs)%8 == 0
            self.pares = np.frombuffer(pares, dtype=np.uint64)
            self.subs  = np.frombuffer(subs,  dtype=np.uint64)
    def db_BLOBs(self):
        p = self.pares.tostring()
        s = self.subs.tostring()
        return p, s

class PlanTime:
    def __init__(self, sta_time='now', end_time='now', use_time=0, sub_time=0,
                 sta_err=0, end_err=0, use_err=0, sub_err=0):
        def now_process(x):
            now = ('now', 'n')
            if x in now:
                return time.time()
            elif isinstance(x, tuple) and x[0] in now:
                return time.time() + x[1]
            else:
                return x
        self.sta_time = now_process(sta_time)
        self.end_time = now_process(end_time)
        self.use_time = use_time
        self.sub_time = sub_time
        self.sta_err = sta_err
        self.end_err = end_err
        self.use_err = use_err
        self.sub_err = sub_err
    def db_nums(self):
        return self.sta_time, self.end_time, self.use_time, self.sub_time,\
               self.sta_err,  self.end_err,  self.use_err,  self.sub_err

class Plan:
    def __init__(self, dbtype:int, name:str, tree_i, p_time, dbid=None):
        self.dbtype = dbtype
        self.name = name
        self.tree_i = tree_i
        self.p_time = p_time
        self.dbid = dbid
        
    def db_item(self):
        ret = [self.dbtype, self.name]
        ret += self.tree_i.db_BLOBs()
        ret += self.p_time.db_nums()
        return ret
    
    def __str__(self):
        dt_obj  = datetime.datetime.fromtimestamp(self.p_time.sta)
        sta_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
        dt_obj  = datetime.datetime.fromtimestamp(self.p_time.end)
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
        
    def db_init(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        sql = '''CREATE TABLE todo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type     INT,   name     TEXT,
            pares    BLOB,  subs     BLOB,
            sta_time REAL,  end_time REAL,  use_time REAL,  sub_time REAL,
            sta_err  REAL,  end_err  REAL,  use_err  REAL,  sub_err  REAL);'''
        self.c.execute(sql)
        self.conn.commit()
        self.conn.close()
        
    def add_aitem(self, plan):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        sql = "INSERT INTO todo VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?);"
        self.c.execute(sql, plan.db_item())
        self.conn.commit()
        self.conn.close()
        
    def get_aitem(self, dbid):
        res = self.c.execute("SELECT * FROM todo WHERE id=?", (dbid,))
        assert len(res) == 13
        return Plan(*res[:3], TreeItem(*res[3:5]), PlanTime(*res[5:]))
    
#test code
if __name__ == '__main__':
    tdb = TODO_db()
    tdb.add_aitem(Plan(1, 'plan1', TreeItem(0), PlanTime('n', ('n', 10), 5)))
