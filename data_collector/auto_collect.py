# -*- coding: utf-8 -*-
import sqlite3
import time
from pickle import loads
import glob

from sqlite_api.argb import ARGB
from sqlite_api.tables import CollTable, CollLogTable


class Collector:
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

    def run_conds(self, cond_dict, num=0):
        """
        :para num:
        0: 0 or 1 collector, if found more than one will raise Error
        1: must 1 collector, if found 0 or more than one will raise Error
        2: any number of collectors
        """
        if 'start_mode' not in cond_dict:
            cond_dict['start_mode'] = ('!=', -1)
        res = self.colls.get_conds_execute(cond_dict, ['id', 'name', 'dump', 't_max'])
        res = list(res)
        if num == 0 and len(res) > 1:
            raise ValueError('num=0, but found {}>1'.format(len(res)))
        if num == 1 and len(res) != 1:
            raise ValueError('num=1, but found {}!=1'.format(len(res)))
        for cid, name, dump, t_max in res:
            coll = loads(dump)
            coll.loads_up(cid, name, t_max)
            coll.try_run(self, self.tdb)

    def run_custom_path(self, coll_cls, source_path):
        cond_dict = {'name': coll_cls.coll_name, 'start_mode': -1}
        res = self.colls.get_conds_onlyone(cond_dict, ['id', 'name', 'dump'], default=None)
        if res is None:
            self.colls.add_item(coll_cls(source_path=''), -1)
            res = self.colls.get_conds_onlyone(cond_dict, ['id', 'name', 'dump'],
                                               default=RuntimeError("can't add custom_path coll"))
        cid, name, dump = res
        coll = loads(dump)
        coll.loads_up(cid, name)
        coll.source_path = source_path
        coll.try_run(self, self.tdb)

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        self.run_conds({'start_mode': 1}, num=2)

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
                self.colls.add_item(coll_obj, start_mode, color)
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
