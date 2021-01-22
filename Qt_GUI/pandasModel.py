# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

import sys
from pickle import dumps

import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

from my_libs.dump_table import DumpTable
from commd_line.init_config import conn

df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                   'b': [100, 200, 300],
                   'c': ['a', 'b', 'c']})


class ColumnSet(dict):
    def __init__(self, default=True, *args, **kwargs):
        self.default = default
        self.fid = None
        self.table = None
        super().__init__(*args, **kwargs)

    def loads_up(self, id, table):
        self.fid = id
        self.table = table

    def is_show(self, name):
        v = self[name]
        if v == 0:
            return self.default
        else:
            return v > 0

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        table = self.table
        delattr(self, 'table')
        table.update_conds({'id': self.fid}, {'dump': dumps(self)})
        self.table = table

    def __getitem__(self, key):
        if key not in self:
            self[key] = 0
        return super().__getitem__(key)


class ColumnSetTable(DumpTable):
    table_name = 'column_set_table'


column_table = ColumnSetTable(conn)


class PandasModel(QAbstractTableModel):
    def __init__(self, data, name):
        QAbstractTableModel.__init__(self)
        self.column_set = column_table.auto_create(ColumnSet, name)
        self._data = data.copy()
        for col in data.columns:
            if not self.column_set.is_show(col):
                self._data.pop(col)

    def rowCount(self, parent=None, *args, **kwargs):
        return self._data.shape[0]

    def columnCount(self, parent=None, *args, **kwargs):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = PandasModel(df, 'all')
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())
