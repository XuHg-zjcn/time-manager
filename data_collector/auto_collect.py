#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os


class Collecter:
    def __init__(self, coll_id, name, enable,
                 table_name, dbtype, source_path, srcipt):
        self.coll_id = coll_id
        self.name = name
        self.enable = enable
        self.command = srcipt + (' --table_name {} --dbtype {} '
            '--source_path {}').format(table_name, dbtype, source_path)

    def run_commd(self):
        os.system(self.command)
        print('{} updated'.format(self.name))


class Collecters(list):
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        cur = self.conn.cursor()
        sql = ('CREATE TABLE IF NOT exists collecters('
               'id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, enable BOOL, '
               'table_name TEXT, dbtype INT, source_path TEXT, srcipt TEXT);')
        cur.execute(sql)
        self.conn.commit()
        cur = self.conn.cursor()
        sql = ('SELECT id, name, enable, table_name, dbtype, '
               'source_path, srcipt FROM collecters;')
        res = cur.execute(sql)
        super().__init__()
        for coll_para in res:
            self.append(Collecter(*coll_para))

    def run_enable(self):
        for coll in self:
            if coll.enable:
                coll.run_commd()

    def add_item(self, name, enable, table_name, dbtype, source_path, srcipt):
        cur = self.conn.cursor()
        sql = ('INSERT INTO collecters'
               '(name, enable, table_name, dbtype, source_path, srcipt)'
               'VALUES(?,?,?,?,?,?);')
        cur.execute(sql, (name, enable, table_name,
                          dbtype, source_path, srcipt))
        self.append(Collecter(None, name, enable, table_name,
                              dbtype, source_path, srcipt))
        self.conn.commit()


def cli():
    import sys
    sys.path.append('../')
    from commd_line.init_config import init_config
    conf = init_config()
    db_path = conf['init']['db_path']
    colls = Collecters(db_path)
    while True:
        inp = input('c:添加, q:退出')
        if inp == 'c':
            colls.add_item(input('name:'),
                           input('enable:').upper() in {'T', 'TRUE', 'Y', 'YES'},
                           input('table_name:'),
                           int(input('dbtype:')),
                           input('source_path:'),
                           input('srcipt:'))
        elif inp == 'q':
            break
        else:
            print('错误, 请重新输入')
            continue
    while True:
        inp = input('u:更新, q:退出')
        if inp == 'u':
            colls.run_enable()
            break
        elif inp == 'q':
            break
        else:
            print('错误, 请重新输入')
            continue
