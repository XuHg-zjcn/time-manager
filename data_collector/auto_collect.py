# -*- coding: utf-8 -*-
import sqlite3
import time
from pickle import loads
import glob

from sqlite_api.argb import ARGB
from sqlite_api.tables import CollTable, CollLogTable


class Collector:
    dbtype = 1000
    table_name = 'browser'
    coll_name = 'Collector'
    plan_name = 'collect'

    def __init__(self, plan_name=plan_name):
        self.plan_name = plan_name
        self.cid = -1
        self.t_max = 0

    def loads_up(self, cid=-1, coll_name=coll_name, t_max=0):
        self.cid = cid
        self.coll_name = coll_name
        self.t_max = t_max

    def run(self, clog, tdb):
        pass

    def try_run(self, clog, tdb):
        try:
            self.run(clog, tdb)
        except sqlite3.OperationalError as e:
            print('Collector {} skip, Error: {}'.format(self.coll_name, e))


class Collectors:
    def __init__(self, conn, tdb, commit_each=True):
        self.conn = conn
        self.tdb = tdb
        self.colls = CollTable(conn)
        self.logs = CollLogTable(conn)
        self.commit_each = commit_each

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        res = self.colls.get_conds_execute({'enable':1}, ['id', 'name', 'dump', 't_max'])
        for cid, name, dump, t_max in res:
            coll = loads(dump)
            coll.loads_up(cid, name, t_max)
            coll.try_run(self, self.tdb)

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

    def add_log(self, cid, t_min, t_max, items, commit=True):
        current_time = time.time()
        cur = self.conn.cursor()
        cur.execute('UPDATE collectors SET runs=runs+1, items=items+?,'
                    't_max=max(t_max,?), t_last=? WHERE id=?', (items, t_max, current_time, cid))
        cur.execute('SELECT runs, name FROM collectors WHERE id=?', (cid,))
        lcur = list(cur)
        if len(lcur) == 0:
            run_i = -1
            name = 'unknown'
        elif len(lcur) == 1:
            run_i, name = lcur[0]
        else:
            raise RuntimeError('not impossible')
        sql = 'INSERT INTO colls_log(cid, run_i, run_time, t_min, t_max, items) VALUES(?,?,?,?,?,?)'
        cur.execute(sql, [cid, run_i, current_time, t_min, t_max, items])
        if commit or self.commit_each:
            self.conn.commit()
        print('Collector {} {} founds'.format(name, items))

    def cli(self):
        from . import defaults
        while True:
            inp = input('a:添加预设, b:一次性, q:退出')
            if inp == 'a':
                coll_obj = defaults.input_choose_coll()()
                enable = self.input_enable()
                color = ARGB.from_str(input('颜色'))
                self.colls.add_item(coll_obj, enable, color)
            elif inp == 'b':
                coll_cls = defaults.input_choose_coll()
                path_glob = input('数据源路径(Glob):')
                paths = glob.glob(path_glob)
                for p in paths:
                    print('Glob matched {}'.format(p))
                    coll_obj = coll_cls(source_path=p)
                    coll_obj.try_run(self, self.tdb)
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
