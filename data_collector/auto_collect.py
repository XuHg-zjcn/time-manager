# -*- coding: utf-8 -*-
from pickle import loads
import glob
from sqlite_api.tables import CollTable, CollLogTable


class Collector:
    dbtype = 1000
    table_name = 'browser'
    coll_name = 'Collector'
    plan_name = 'collect'

    def __init__(self, plan_name=plan_name):
        self.plan_name = plan_name

    def loads_up(self, cid=-1, coll_name=coll_name):
        self.cid = cid
        self.coll_name = coll_name

    def run(self, clog, tdb):
        pass


class Collectors:
    def __init__(self, conn, tdb):
        self.conn = conn
        self.tdb = tdb
        self.colls = CollTable(conn)
        self.logs = CollLogTable(conn)

    # TODO: check is already add in sqlite, use a table collect history
    def run_enable(self):
        res = self.colls.get_conds_execute({'enable':1}, ['id', 'name', 'dump'])
        for cid, name, dump in res:
            coll = loads(dump)
            coll.loads_up(cid, name)
            coll.run(self.logs, self.tdb)

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
                self.colls.add_item(coll_obj, enable)
            elif inp == 'b':
                coll_cls = defaults.input_choose_coll()
                path_glob = input('数据源路径(Glob):')
                paths = glob.glob(path_glob)
                for p in paths:
                    print('Glob matched {}'.format(p))
                    coll_obj = coll_cls(source_path=p)
                    coll_obj.run(self.logs, self.tdb)
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
