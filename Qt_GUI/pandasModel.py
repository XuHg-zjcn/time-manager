# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

from enum import Enum
from pickle import dumps

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QSpinBox, QWidget, QTableView

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

    def on_active(self, qmi, data):
        """should return QWidget"""
        print('active', qmi, data)

    def on_edit_finish(self, qmi, widget):
        """should return value of `widget`"""
        print('edit_finish', qmi, widget)


class TableColumnSpinBox(TableColumn):
    def on_active(self, qmi, data):
        spb = QSpinBox()
        spb.setValue(int(data))
        return spb

    def on_edit_finish(self, qmi, widget):
        try:
            return widget.value()
        except RuntimeError:
            return None


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


class iTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_edit_index = None
        self.current_edit_widget = None
        self.column_set = None

    def setDataFrame(self, dataframe, name, column_set_cls=ColumnSet):
        # filter columns
        column_set = column_table.auto_create(column_set_cls, name)
        self.column_set = column_set
        data2 = dataframe.copy()
        for col_name in data2.columns:
            if not column_set.is_show(col_name):
                data2.pop(col_name)
        # PandasModel
        model = PandasModel(data2)
        self.setModel(model)
        self.on_builds()
        self.set_wides()
        # connect signals, TODO: edit in TabView, write to database.
        try: self.activated.disconnect()
        except TypeError: pass  # error when without connect before disconnect
        try: self.pressed.disconnect()
        except TypeError: pass  # error when without connect before disconnect
        self.activated.connect(lambda x: self.active_slot(x))
        self.pressed.connect(lambda x: self.pressed_slot(x))
        headers = self.horizontalHeader()
        headers.sectionResized.connect(self.resized_slot)

    def on_builds(self):
        if not hasattr(self, 'column_set'):
            return
        model = self.model()
        for i in range(model.columnCount()):
            col_name = model.headerData(i, Qt.Horizontal, role=Qt.DisplayRole)
            for j in range(model.rowCount()):
                qmi = model.index(j, i)
                data = model.data(qmi)
                widget = self.column_set[col_name].on_build(data)
                if isinstance(widget, QWidget):
                    self.setIndexWidget(qmi, widget)

    def set_wides(self):
        if not self.column_set:
            return
        model = self.model()
        i2name = map(lambda x:model.headerData(x, Qt.Horizontal, role=Qt.DisplayRole),
                     range(model.columnCount()))
        for i, col_name in enumerate(i2name):
            self.setColumnWidth(i, self.column_set[col_name].wide)

    def active_slot(self, qmi):
        if not self.column_set:
            return
        col = qmi.column()
        model = self.model()
        col_name = model.headerData(col, Qt.Horizontal, role=Qt.DisplayRole)
        data = model.data(qmi)
        widget = self.column_set[col_name].on_active(qmi, data)
        if isinstance(widget, QWidget):
            self.setIndexWidget(qmi, widget)
            self.current_edit_index = qmi
            self.current_edit_widget = widget

    def pressed_slot(self, qmi):
        if not self.column_set:
            return
        col = qmi.column()
        model = self.model()
        col_name = model.headerData(col, Qt.Horizontal, role=Qt.DisplayRole)
        if self.current_edit_widget and self.current_edit_index:
            cew = self.current_edit_widget
            cei = self.current_edit_index
            col_old = cei.column()
            name_old = model.headerData(col_old, Qt.Horizontal, role=Qt.DisplayRole)
            value = self.column_set[name_old].on_edit_finish(qmi, cew)
            print('edit_finish', name_old, value)
            self.setIndexWidget(cei, None)
            self.current_edit_widget = None
            self.current_edit_index = None

    def resized_slot(self, i, _, w):
        if not self.column_set:
            return
        col_name = self.model().headerData(i, Qt.Horizontal, role=Qt.DisplayRole)
        self.column_set.set_wide(col_name, w)
