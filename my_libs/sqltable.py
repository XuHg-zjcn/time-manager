from collections import Iterable
from numbers import Number

import pandas as pd
import numpy as np


def number_np2py(x):
    if isinstance(x, np.integer):
        x = int(x)
    elif isinstance(x, np.floating):
        x = float(x)
    return x


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
        """
        commit change to sqlite3 database.
        don't use in class method, please use 'self.conn.commit()'
        """
        if self.commit_each:
            raise RuntimeWarning('commit each change is Enable')
        self.conn.commit()

    @staticmethod
    def _fields2sql(fields=None):
        if isinstance(fields, str):
            fields_str = fields  # only one field, return without tuple
        elif isinstance(fields, Iterable):
            fields_str = ', '.join(fields)
        elif not fields:
            fields_str = '*'
        else:
            raise ValueError('invalid fields')
        return fields_str

    @staticmethod
    def _conds2where(cond_dict):
        """
        if cond_dict is empty, return empty string
        not empty dict, return string include 'WHERE'
        """
        if not cond_dict:
            return ''
        sql = 'WHERE '
        paras = []
        for key, value in cond_dict.items():
            value = number_np2py(value)
            if value is None:
                continue
            elif type(value) in [bool, int, float, str]:  # x == ?
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

    def conds_sql(self, cond_dict=None, fields=None):
        """
        Get Plans matched conditions.
        :para cond_dict: {'field1':value, 'field2':(min, max), 'field3':('<', value), ...}
        """
        fields_str = self._fields2sql(fields)
        where_str, paras = self._conds2where(cond_dict)
        sql = 'SELECT {} FROM {} {}'.format(fields_str, self.table_name, where_str)
        return sql, paras

    def get_conds_execute(self, cond_dict=None, fields=None):
        cur = self.conn.cursor()
        sql, paras = self.conds_sql(cond_dict, fields)
        res = cur.execute(sql, paras)
        if isinstance(fields, str):
            return map(lambda x: x[0], res)
        else:
            return res

    def get_conds_onlyone(self, cond_dict, fields=None,
                          def0=LookupError('not found'),
                          def2=LookupError('found multiply items')):
        def raise_return(x):
            if isinstance(x, Exception):
                raise x
            else:
                return x

        cur = self.get_conds_execute(cond_dict, fields)
        lst = list(cur)
        if len(lst) == 0:
            return raise_return(def0)
        elif len(lst) == 1:
            return lst[0]
        else:
            return raise_return(def2)

    def get_conds_dataframe(self, cond_dict=None, fields=None):
        sql, paras = self.conds_sql(cond_dict, fields)
        return pd.read_sql_query(sql, self.conn, params=paras)

    def _update2sql(self, update_dict):
        sqls = []
        paras = []
        for key, value in update_dict.items():
            value = number_np2py(value)
            if isinstance(value, Number) or \
               isinstance(value, str) or \
               isinstance(value, bytes):
                sqls.append("{}=?".format(key))
                paras.append(value)
            elif isinstance(value, tuple) and len(value) == 2:
                if value[0] in ['+', '-', '*', '/']:
                    sqls.append("{}={}{}?".format(key, key, value[0]))
                    paras.append(value[1])
        return ', '.join(sqls), paras

    def update_conds(self, cond_dict, update_dict, commit=None):
        cur = self.conn.cursor()
        where_str, paras1 = self._conds2where(cond_dict)
        set_str, paras2 = self._update2sql(update_dict)
        sql = 'UPDATE {} SET {} {}'.format(self.table_name, set_str, where_str)
        cur.execute(sql, paras2+paras1)
        if self.commit_each or commit:
            self.conn.commit()

    def delete(self, cond_dict, commit=None):
        cur = self.conn.cursor()
        where_str, paras = self._conds2where(cond_dict)
        sql = 'DELETE FROM {} {}'.format(self.table_name, where_str)
        cur.execute(sql, paras)
        if self.commit_each or commit:
            self.conn.commit()

    def __del__(self):
        """
        auto commit when del SqlTable obj.
        """
        if not self.commit_each:
            self.conn.commit()
