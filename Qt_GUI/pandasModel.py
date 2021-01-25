# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

from enum import Enum
from pickle import dumps

from PyQt5.QtCore import QAbstractTableModel, Qt

from my_libs.dump_table import DumpTable
from commd_line.init_config import conn


class ShowStat(Enum):
    No = 0
    Default = 1
    Yes = 2


class TableColumn:
    def __init__(self, is_show: ShowStat, wide: int):
        self.is_show = is_show
        self.wide = wide

    def __repr__(self):
        return "TableColumn({}, {})".format(self.is_show, self.wide)

    __str__ = __repr__


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
        v = self[name].is_show
        if v == ShowStat.Default:
            return self.default
        else:
            return v == ShowStat.Yes

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if hasattr(self, 'table'):  # don't run in pickle.loads
            table = self.table      # else raise AttributeError
            delattr(self, 'table')
            table.update_conds({'id': self.fid}, {'dump': dumps(self)})
            self.table = table

    def __getitem__(self, key):
        if key not in self:
            self[key] = TableColumn(ShowStat.Default, 80)
        return super().__getitem__(key)

    def set_show(self, name, is_show):
        wide = self[name].wide
        self[name] = TableColumn(is_show, wide)

    def set_wide(self, name, wide):
        is_show = self[name].is_show
        self[name] = TableColumn(is_show, wide)


class ColumnSetTable(DumpTable):
    table_name = 'column_set_table'


column_table = ColumnSetTable(conn, commit_each=True)


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

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


def pandas_table(tableview, dataframe, name):
    column_set = column_table.auto_create(ColumnSet, name)
    data2 = dataframe.copy()
    for col_name in data2.columns:
        if not column_set.is_show(col_name):
            data2.pop(col_name)
    model = PandasModel(data2)
    tableview.setModel(model)
    for i, col_name in enumerate(data2.columns):
        tableview.setColumnWidth(i, column_set[col_name].wide)
    headers = tableview.horizontalHeader()
    i2name = list(data2.columns)
    headers.sectionResized.connect(lambda i,_,w: column_set.set_wide(i2name[i], w))
