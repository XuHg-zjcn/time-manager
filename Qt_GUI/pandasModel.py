# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

from enum import Enum
from pickle import dumps

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QSpinBox

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

    def on_build(self, value):
        pass

    def on_active(self, q_model_index):
        pass

    def on_entered(self, q_model_index):
        pass


class TableColumnSpinBox(TableColumn):
    def on_build(self, value):
        spb = QSpinBox()
        spb.setValue(int(value))
        return spb


class ColumnSet(dict):
    def __init__(self, default=True, *args, **kwargs):
        self.i2name = None
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
            if table is None:
                return
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

    def on_builds(self, tableview):
        model = tableview.model()
        self.i2name = list(map(model.headerData, range(model.columnCount())))
        for i in range(model.columnCount()):
            col_name = model.headerData(i)
            for j in range(model.rowCount()):
                qmi = model.index(j, i)
                data = model.data(qmi)
                widget = self[col_name].on_build(data)
                if widget is not None:
                    tableview.setIndexWidget(qmi, widget)

    def set_wides(self, tableview):
        if self.i2name is None:
            raise RuntimeError('please call `on_builds` before `set_wides`')
        for i, col_name in enumerate(self.i2name):
            tableview.setColumnWidth(i, self[col_name].wide)

    def actived_slot(self, q_model_index):
        print(q_model_index)

    def entered_slot(self, q_model_index):
        print(q_model_index)

    def resized_slot(self, i, _, w):
        self.set_wide(self.i2name[i], w)


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

    def headerData(self, col, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


def pandas_table(tableview, dataframe, name, column_set_cls=ColumnSet):
    # filter columns
    column_set = column_table.auto_create(column_set_cls, name)
    data2 = dataframe.copy()
    for col_name in data2.columns:
        if not column_set.is_show(col_name):
            data2.pop(col_name)
    # PandasModel
    model = PandasModel(data2)
    tableview.setModel(model)
    column_set.on_builds(tableview)
    column_set.set_wides(tableview)
    # connect signals, TODO: edit in TabView, write to database.
    tableview.activated.connect(lambda x: column_set.actived_slot(x))
    headers = tableview.horizontalHeader()
    headers.sectionResized.connect(column_set.resized_slot)
