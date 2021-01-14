import time
from pickle import dumps
from sqlite_api.task_db import SqlTable


class CollTable(SqlTable):
    name2dtype = [('name', 'TEXT'), ('enable', 'BOOL'), ('dump', 'BLOB'),
                  ('runs', 'INT'), ('items', 'INT')]
    table_name = 'collectors'

    def add_item(self, coll_obj, enable=True, commit=True):
        self.insert([coll_obj.coll_name, enable, dumps(coll_obj), 0, 0], commit)


class CollLogTable(SqlTable):
    name2dtype = [('cid', 'INT'), ('run_i', 'INT'), ('run_time', 'DATETIME'),
                  ('t_min', 'DATETIME'), ('t_max', 'DATETIME')]
    table_name = 'colls_log'

    def add_log(self, cid, t_min, t_max, items, commit=True):
        cur = self.conn.cursor()
        cur.execute('UPDATE collectors SET runs=runs+1, items=items+? WHERE id=?', (items, cid))
        cur.execute('SELECT runs, name FROM collectors WHERE id=?', (cid,))
        lcur = list(cur)
        if len(lcur) == 0:
            raise ValueError('cid invalid')
        elif len(lcur) == 1:
            run_i, name = lcur[0]
        else:
            raise RuntimeError('not impossible')
        sql = 'INSERT INTO colls_log(cid, run_i, run_time, t_min, t_max, items) VALUES(?,?,?,?,?,?)'
        cur.execute(sql, [cid, run_i, time.time(), t_min, t_max, items])
        if commit or self.commit_each:
            self.commit()
        print('Collector {} {} founds'.format(name, items))
