import sqlite3
import math
import time_algh
import os

convS_063 = 1*3600   #short time
convS_Max = 30/60

convL_063 = 2*86400  #long time
convL_Max = 4/24

mean_duty = 3/24     #integral of inf time
integ_sec = 3*86400  #max int error

Ton_sec   = 15*60    #15min
Toff_sec  = 2*3600   #2h

class sqlite_api:
    def __init__(self, db_path):
        self.db_path = db_path
        self.item = []
        if not os.path.exists(db_path):
            self.db_init()
        self.get_data()
        
    def db_init(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        sql = '''CREATE TABLE meta(
            id int,
            type int,
            name text,
            para real,
            min real,
            max real,
            curr real);'''
        c.execute(sql)
        c.execute("INSERT INTO meta VALUES(0, 0, 'T_on' , ?, 0, ?, 0);", (0,         Ton_sec  ))
        c.execute("INSERT INTO meta VALUES(1, 0, 'T_off', ?, 0, ?, 0);", (0,         Toff_sec ))
        c.execute("INSERT INTO meta VALUES(2, 1, 'integ', ?, ?, ?, 0);", (mean_duty, -integ_sec, integ_sec))
        c.execute("INSERT INTO meta VALUES(3, 2, 'convS', ?, 0, ?, 0);", (convS_063, convS_Max))
        c.execute("INSERT INTO meta VALUES(4, 2, 'convL', ?, 0, ?, 0);", (convL_063, convL_Max))
        conn.commit()
        conn.close()
        
    def get_data(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        sel = c.execute("SELECT * FROM meta;")
        for row in sel:
            if row[1] == 0:
                self.item.append(time_algh.min_max(row[0], row[4], row[5]))
            elif row[1] == 1:
                self.item.append(time_algh.mean_integ(row[0], row[3], row[4], row[5], row[6]))
            elif row[1] == 2:
                self.item.append(time_algh.t_conv(row[0], row[3], row[4], row[5], row[6]))
        conn.commit()
        conn.close()

    def update(self, event):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        isOK = True
        tmin = float('-inf')  #next event alloc
        tmax = float('inf')
        for i in self.item:
            V1, tr, isOK101 = i.update(event)
            if isOK101 != 0:
                isOK = False
            c.execute("UPDATE meta SET curr = ? WHERE id = ?", (V1, i.idx))
            if tr[0] > tmin:
                tmin = tr[0]
            if tr[1] < tmax:
                tmax = tr[1]
        conn.commit()
        conn.close()
        return (tmin, tmax), isOK
        
