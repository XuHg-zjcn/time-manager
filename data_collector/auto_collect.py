# -*- coding: utf-8 -*-
import time
import glob
from pickle import dumps, loads


class Collector:
    dbtype = 1000
    table_name = 'browser'
    coll_name = 'Collector'

    def __init__(self, source_path, plan_name='collect'):
        self.source_path = source_path
        self.plan_name = plan_name

    def write_log(self, tdb, cid, t_min, t_max, items):
        """run once d=-1"""
        cur = tdb.conn.cursor()
        cur.execute('UPDATE collectors SET runs=runs+1, items=items+? WHERE id=?', (items, cid))
        try:
            run_i, name = list(cur.execute('SELECT runs, name FROM collectors WHERE id=?',(cid,)))[0]
        except IndexError:
            run_i = -1
            name = self.coll_name
        cur.execute('INSERT INTO colls_log (cid, run_i, run_time, t_min, t_max, items) VALUES(?,?,?,?,?,?)',
                    (cid, run_i, time.time(), t_min, t_max, items))
        print('{} {} items updated'.format(name, items))
        tdb.conn.commit()

    def run(self, tdb, cid):
        self.write_log(tdb, cid, None, None, 0)
        pass


class Collectors:
    def __init__(self, tdb):
        self.tdb = tdb
        cur = self.tdb.conn.cursor()
        sql = ('CREATE TABLE IF NOT exists collectors('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT, enable BOOL, dump BLOB, runs INT, items INT);')
        cur.execute(sql)
        sql = ('CREATE TABLE IF NOT exists colls_log('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'cid INT, run_i INT, run_time REAL, t_min REAL, t_max REAL, items INT);')
        cur.execute(sql)
        self.tdb.conn.commit()

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        cur = self.tdb.conn.cursor()
        res = cur.execute('SELECT id, dump FROM collectors WHERE enable=1')
        for cid, dump in res:
            coll = loads(dump)
            coll.run(self.tdb, cid)

    def add_item(self, name, enable, coll):
        cur = self.tdb.conn.cursor()
        sql = 'INSERT INTO collectors (name, enable, dump, runs, items) VALUES(?,?,?,0,0);'
        cur.execute(sql, (name, enable, dumps(coll)))
        sql = 'SELECT last_insert_rowid() FROM collectors WHERE id=1'
        cid = list(cur.execute(sql))[0]
        self.tdb.conn.commit()

    @classmethod
    def input_enable(cls):
        while True:
            enable = input('enable:').upper()
            if enable in {'Y', 'YES', 'T', 'TRUE'}:
                return True
            elif enable in {'N', 'NO', 'F', 'FALSE'}:
                return False
            else:
                continue

    def cli(self):
        from . import defaults
        while True:
            inp = input('a:添加预设, b:一次性, q:退出')
            if inp == 'a':
                coll_obj = defaults.input_choose_coll()()
                enable = self.input_enable()
                self.add_item(coll_obj.coll_name, enable, coll_obj)
            elif inp == 'b':
                coll_cls = defaults.input_choose_coll()
                path_glob = input('数据源路径(Glob):')
                paths = glob.glob(path_glob)
                for p in paths:
                    print('Glob matched {}'.format(p))
                    coll_obj = coll_cls(source_path=p)
                    coll_obj.run(self.tdb, -1)
            elif inp == 'q':
                break
            else:
                print('错误, 请重新输入')
                continue
        while True:
            inp = input('u:更新, q:退出')
            if inp == 'u':
                self.run_enable()
                break
            elif inp == 'q':
                break
            else:
                print('错误, 请重新输入')
                continue
