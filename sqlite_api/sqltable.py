from collections import Iterable

import pandas as pd
import numpy as np


class SqlTable:
    name2dtype = [('example_int', 'INT'), ('example_text', 'TEXT')]
    table_name = 'table_name'

    def __init__(self, conn, commit_each=False):
        """
        Examples
        --------
        table_name: 'tab'
        name2type_dict: [('name','TEXT'), ('num','REAL')]
        """
        self.conn = conn
        self.commit_each = commit_each
        self.create_table(commit=True)

    def create_table(self, commit=True):
        cur = self.conn.cursor()
        fields = []
        for name, dtype in self.name2dtype:
            if dtype:
                fields.append('{} {}'.format(name, dtype))
            else:
                fields.append(str(name))
        fields = ', '.join(fields)
        sql = 'CREATE TABLE IF NOT exists {}('\
              'id INTEGER PRIMARY KEY AUTOINCREMENT, {})'
        cur.execute(sql.format(self.table_name, fields))
        if commit or self.commit_each:
            self.conn.commit()

    def insert(self, values, commit=None):
        cur = self.conn.cursor()
        if not isinstance(values, dict):
            val_d = {}
            for v, (k, _) in zip(values, self.name2dtype):
                val_d[k] = v
        else:
            val_d = values
        sql = 'INSERT INTO {}({}) VALUES({})'
        sqf = sql.format(self.table_name,
                         ', '.join(val_d.keys()),
                         ('?,'*len(val_d))[:-1])
        cur.execute(sqf, list(val_d.values()))
        if commit or self.commit_each:
            self.conn.commit()

    def commit(self):
        if self.commit_each:
            raise RuntimeWarning('commit each change is Enable')
        self.conn.commit()

    def conds_sql(self, cond_dict, fields=None):
        """
        Get Plans matched conditions.
        :para cond_dict: {'field1':value, 'field2':(min, max), 'field3':('<', value), ...}
        """
        if isinstance(fields, str):
            fields_str = fields  # only one field, return without tuple
        elif isinstance(fields, Iterable):
            fields_str = ', '.join(fields)
        elif not fields:
            fields_str = '*'
        else:
            raise ValueError('invalid fields')
        sql = 'SELECT {} FROM {} WHERE '.format(fields_str, self.table_name)
        paras = []
        assert len(cond_dict) > 0
        for key, value in cond_dict.items():
            if isinstance(value, np.integer):
                value = int(value)
            elif isinstance(value, np.floating):
                value = float(value)
            if value is None:
                continue
            elif type(value) in [bool, int, float]:   # x == ?
                sql += '{}=? and '.format(key)
                paras.append(value)
            elif isinstance(value, tuple) and len(value) == 2:  # a <= x < b
                if type(value[0]) in [int, float]:
                    sql += '?<={0} and {0}<? and '.format(key)
                    paras += value
                elif value[0] in ['<', '>', '>=', '<=', '=', '==', '!=']:
                    sql += '{}{}? and '.format(key, value[0])
                    paras.append(value[1])
                else:
                    raise ValueError('invalid tuple {}'.format(value))
            else:
                raise ValueError('invalid value type {}'.format(type(value)))
        sql = sql[:-5]  # remove end of str ' and '
        return sql, paras

    def get_conds_execute(self, cond_dict, fields=None):
        cur = self.conn.cursor()
        sql, paras = self.conds_sql(cond_dict, fields)
        res = cur.execute(sql, paras)
        if isinstance(fields, str):
            return map(lambda x: x[0], res)
        else:
            return res

    def get_conds_onlyone(self, cond_dict, fields=None, default=None):
        cur = self.get_conds_execute(cond_dict, fields)
        lst = list(cur)
        if len(lst) == 0:
            if isinstance(default, Exception):
                raise default
            else:
                return default
        elif len(lst) == 1:
            return lst[0]
        else:
            raise LookupError('found multiply({}) items'.format(len(lst)))

    def get_conds_dataframe(self, cond_dict, fields=None):
        sql, paras = self.conds_sql(cond_dict, fields)
        return pd.read_sql_query(sql, self.conn, params=paras)
