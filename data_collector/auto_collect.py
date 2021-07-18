# -*- coding: utf-8 -*-
import sqlite3
import time
import glob

from my_libs.argb import ARGB
from my_libs.dump_table import DumpBaseCls
from sqlite_api.tables import colls, logs


class Collector(DumpBaseCls):
    names_autoload = {'id', 'table', 'name', 't_max'}

    def run(self):
        #    t_min, t_max, items
        return None, None, 0

    def try_run(self):
        try:
            return self.run()
        except sqlite3.OperationalError as e:
            print('Collector {} skip, Error: {}'.format(self.db_fields['name'], e))
            return None, None, 0


# TODO: op collect table via class
class Collectors:
    def __init__(self, conn, commit_each=True):
        self.conn = conn                # don't remove para `conn`,
        self.commit_each = commit_each  # it can mind you need operate database

    def run_obj(self, obj):
        t_min, t_max, items = obj.try_run()
        cid = obj.db_fields['id']
        self.add_log(cid, t_min, t_max, items, commit=True)

    def run_custom_path(self, coll_cls, source_path):
        cond_dict = {'name': coll_cls.name, 'start_mode': -1}
        res = colls.get_conds_objs(cond_dict)
        if len(res) == 0:
            colls.add_obj(coll_cls(source_path=''), -1)
            res = colls.get_conds_objs(cond_dict)
        elif len(res) > 1:
            raise LookupError('found more than one')
        coll = res[0]
        coll.db_fields['t_max'] = 0
        coll.source_path = source_path
        self.run_obj(coll)

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        objs = colls.get_conds_objs({'start_mode': 1})
        for obj in objs:
            self.run_obj(obj)

    def add_log(self, cid, t_min, t_max, items, commit=True):
        current_time = time.time()
        cur = self.conn.cursor()
        cur.execute('UPDATE collectors SET runs=runs+1, items=items+:its,'
                    't_max=max(ifnull(t_max,:tm2), ifnull(:tm2,t_max)), t_last=:ts WHERE id=:id',
                    {'its':items, 'tm2':t_max, 'ts':current_time, 'id':cid})
        cur.execute('SELECT runs, name FROM collectors WHERE id=?', (cid,))
        lcur = list(cur)
        if len(lcur) == 0:
            run_i = -1
            name = 'unknown'
        elif len(lcur) == 1:
            run_i, name = lcur[0]
        else:
            raise RuntimeError('not impossible')
        logs.insert([cid, run_i, current_time, t_min, t_max, items])
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
                colls.add_obj(coll_obj, start_mode)
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
