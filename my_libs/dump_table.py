import time
from pickle import loads, dumps

from my_libs.sqltable import SqlTable, onlyone_process


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
            vns = obj.names_autoload.copy()
            assert 'id' in vns, "'id' must in names_autoload"
            table = 'table' in vns and not vns.remove('table')
            paras = self.get_conds_onlyone_dict({'id': did}, vns)
            if table:
                paras['table'] = self
            obj.loads_up(paras)
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
            self.plus1(obj.db_fields['id'])

    def add_obj(self, obj, commit=True):
        """
        don't use obj after call the func, please cal get_conds_objs,
        because obj.db_fields will remove,
        obj.db_fields maybe has different between load from db with before call the method.
        """
        v_d = obj.dumps_dn()
        v_d['dump'] = dumps(obj)  # warning: direct modified
        if 'name' not in v_d:
            v_d['name'] = obj.__class__.__name__
        if 'runs' not in v_d:
            v_d['runs'] = 0
        self.insert(v_d, commit)

    def update_obj(self, obj, cond_dict=None, commit=None):
        v_d = obj.dumps_dn()  # can't dump some attributes
        dump = dumps(obj)
        obj.loads_up(v_d)
        v_d2 = v_d.copy()
        v_d2['dump'] = dump
        'id' in v_d2 and v_d2.pop('id')
        'table' in v_d2 and v_d2.pop('table')
        cond_dict = cond_dict or {'id': v_d['id']}
        assert len(self.get_conds_execute(cond_dict, 'id')) == 1
        self.update_conds(cond_dict, v_d2, commit)

    def name_auto_insert_or_update(self, obj):
        name = obj.db_fields['name']
        get = self.get_conds_onlyone({'name': name}, 'id', def0=None)
        if get is None:
            self.add_obj(obj)
        else:
            self.update_obj(obj, {'name': name})

    def plus1(self, did):
        cur = self.conn.cursor()
        cur.execute('UPDATE {} SET runs=runs+1, t_last=? WHERE id=?'\
                    .format(self.table_name), (time.time(), did))

    def auto_create(self, a_cls, name, commit=True):
        objs = self.get_conds_objs({'name': name})
        if len(objs) == 0:
            obj = a_cls(name=name)
            self.add_obj(obj, commit)
            objs = self.get_conds_objs({'name': name})
        obj = onlyone_process(objs)
        assert isinstance(obj, a_cls), "get obj isn't instance of a_cls"
        return obj


class DumpBaseCls:
    names_autoload = {'id', 'table', 'name'}

    def __init__(self, name):
        self.db_fields = {'name': name}

    def loads_up(self, db_fields):
        self.db_fields = db_fields

    def dumps_dn(self):
        ret = self.db_fields
        delattr(self, 'db_fields')
        return ret

    def update_to_db(self, commit=None):
        if hasattr(self, 'db_fields') and\
           'table' in self.db_fields and\
           'id' in self.db_fields:
            self.db_fields['table'].update_obj(self, commit)
