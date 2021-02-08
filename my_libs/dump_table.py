import time
from pickle import loads, dumps

from my_libs.sqltable import SqlTable


class DumpTable(SqlTable):
    name2dtype = [('name', 'TEXT'),   # name of collector
                  ('dump', 'BLOB'),   # pickle.dumps bytes
                  ('runs', 'INT'),    # runs counts
                  ('t_last', 'REAL'), # timestamp of last run
                  ('color', 'INT')]   # color for plot
    table_name = 'dump_table'

    """
    this methods of object will called in module, if not found will skip:
    loads_up: called in load from database, paras are table fields
    dumps_dn: called in dump to database, return a dict of fields
    """

    def get_conds_objs(self, cond_dict):
        id_dumps = self.get_conds_execute(cond_dict, ['id', 'dump'])
        objs = []
        for did, dump in id_dumps:
            obj = loads(dump)
            if hasattr(obj, 'loads_up'):
                vns = list(obj.loads_up.__code__.co_varnames)
                vns.remove('self')
                if 'table' in vns:  # var name 'table' will into self
                    table_index = vns.index('table')
                    vns.remove('table')
                else:
                    table_index = None
                paras = list(self.get_conds_onlyone({'id': did}, vns))
                if table_index is not None:
                    paras.insert(table_index, self)
                obj.loads_up(*paras)
                obj.did = did
            objs.append(obj)
        return objs

    def run_conds_objs(self, cond_dict, num=0, f_name='run', paras=()):
        objs = self.get_conds_objs(cond_dict)
        if num == 0 and len(objs) > 1:
            raise ValueError('num=0, but found {}>1'.format(len(objs)))
        if num == 1 and len(objs) != 1:
            raise ValueError('num=1, but found {}!=1'.format(len(objs)))
        for obj in objs:
            getattr(obj, f_name)(*paras)
            self.plus1(obj.did)

    def add_obj(self, obj, commit=True):
        if hasattr(obj, 'dumps_dn'):
            v_d = obj.dumps_dn()
        else:
            v_d = {}
        dump = dumps(obj)
        v_d['dump'] = dump
        if 'name' not in v_d:
            v_d['name'] = obj.__class__.__name__
        if 'runs' not in v_d:
            v_d['runs'] = 0
        self.insert(v_d, commit)

    def plus1(self, did):
        cur = self.conn.cursor()
        cur.execute('UPDATE {} SET runs=runs+1, t_last=? WHERE id=?'\
                    .format(self.table_name), (time.time(), did))

    def auto_create(self, a_cls, name, commit=True):
        objs = self.get_conds_objs({'name': name})
        if len(objs) == 0:
            obj = a_cls()
            v_d = {'name': name, 'dump': dumps(obj), 'runs': 0}
            self.insert(v_d, commit)
            objs = self.get_conds_objs({'name': name})
            assert len(objs) == 1
        elif len(objs) > 1:
            raise ValueError('found more than one items')
        return objs[0]
