# -*- coding: utf-8 -*-
import sqlite3
import time
import glob

from my_libs.argb import ARGB
from sqlite_api.tables import CollTable, CollLogTable


class Collector:
    table_name = 'browser'
    name = 'Collector'
    plan_name = 'collect'

    def __init__(self, plan_name=plan_name):
        self.plan_name = plan_name
        self.cid = -1
        self.t_max = 0

    def loads_up(self, id=-1, name=name, t_max=0):
        self.cid = id
        self.name = name
        self.t_max = t_max

    def run(self, clog, tdb):
        pass

    def try_run(self, clog, tdb):
        try:
            self.run(clog, tdb)
        except sqlite3.OperationalError as e:
            print('Collector {} skip, Error: {}'.format(self.name, e))


class Collectors:
    def __init__(self, conn, tdb, commit_each=True):
        self.conn = conn
        self.tdb = tdb
        self.colls = CollTable(conn)
        self.logs = CollLogTable(conn)
        self.commit_each = commit_each

    def run_custom_path(self, coll_cls, source_path):
        cond_dict = {'name': coll_cls.name, 'start_mode': -1}
        res = self.colls.get_conds_objs(cond_dict)
        if len(res) == 0:
            self.colls.add_obj(coll_cls(source_path=''), -1)
            res = self.colls.get_conds_objs(cond_dict)
        elif len(res) > 1:
            raise LookupError('found more than one')
        coll = res[0]
        coll.source_path = source_path
        coll.try_run(self, self.tdb)

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        self.colls.run_conds_objs({'start_mode': 1}, num=2,
                                  f_name='try_run', paras=(self, self.tdb))

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
        self.logs.insert([cid, run_i, current_time, t_min, t_max, items])
        if commit or self.commit_each:
            self.conn.commit()
        print('Collector {} {} founds'.format(name, items))

    def cli(self):
        from . import defaults
        while True:
            inp = input('a:添加预设, b:一次性, q:退出')
            if inp == 'a':
                coll_obj = defaults.input_choose_coll()()
                start_mode = int(input('启动方式(0手动,1批量,2自动):'))
                color = ARGB.from_str(input('颜色'))
                self.colls.add_obj(coll_obj, start_mode)
            elif inp == 'b':
                coll_cls = defaults.input_choose_coll()
                path_glob = input('数据源路径(Glob):')
                paths = glob.glob(path_glob)
                for p in paths:
                    print('Glob matched {}'.format(p))
                    self.run_custom_path(coll_cls, p)
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
