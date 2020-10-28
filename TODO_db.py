import sqlite3
import struct
import os
import time
import datetime

class plan_time:
    def __init__(self, start=None, during=0, end=0, start_err=0, during_err=0, end_err=0):
        if start is None:
            self.start = time.time()
        else:
            self.start = start
        self.during = during
        self.end = end
        self.start_err = start_err
        self.during_err = during_err
        self.end_err = end_err
    def get(self):
        return self.start, self.during, self.end, self.start_err, self.during_err, self.end_err

class plan:
    def __init__(self, dbid, name, p_time):
        self.dbid = dbid
        self.name = name
        self.p_time = p_time
        
    def __str__(self):
        dateArray = datetime.datetime.fromtimestamp(self.p_time.start)
        start_str = dateArray.strftime('%Y-%m-%d %H:%M:%S')
        timedelta = datetime.timedelta(seconds=self.p_time.during)
        timedelta = str(timedelta)
        if p_time.start_err != 0:
            start_str += '+={}'.format(timedelta)
        return 'name:{}, start:{}, end:{}, during:{}'.format(self.name, start_str, end_str, during_str)

class TODO_db:
    def __init__(self, db_path):
        self.db_path = db_path
        if not os.path.exists(db_path):
            self.db_init()
        
    def db_init(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        sql = '''CREATE TABLE todo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type       INT,
            name       TEXT,
            n_pare     INT,
            n_sub      INT,
            pares      BLOB,
            subs       BLOB,
            start      REAL,
            during     REAL,
            end        REAL,
            start_err  REAL,
            during_err REAL,
            end_err    REAL);'''
        self.c.execute(sql)
        self.add_aitem(plan('root', None, plan_time()), [0])
        self.conn.commit()
        self.conn.close()
        
    def update(self, planx, pare_ids):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        self.add_aitem(planx, pare_ids)
        self.conn.commit()
        self.conn.close()
        
    def add_aitem(self, planx, pare_ids):
        if planx.dbid is None:
            n_pare = 0
            pare_bytes = b''
        else:
            n_pare = len(planx.pare_ids)
            pare_bytes = struct.pack('>%dI'%n_pare, *pare_ids)
        self.c.execute("INSERT INTO todo VALUES(NULL, 0, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?);", 
                       (planx.name, pare_bytes, b'', *planx.p_time.get()))
   
    def get_things(Smin, Smax):
        self.c.execute("SELECT ?<start<? FROM todo", (Smin, Smax))

