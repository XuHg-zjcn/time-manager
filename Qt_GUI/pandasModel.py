# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

from enum import Enum

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QSpinBox, QWidget, QTableView, QMenu

from my_libs.dump_table import DumpTable, DumpBaseCls
from commd_line.init_config import conn
from my_libs.sqltable import SqlTable


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


class ColumnSet(dict, DumpBaseCls):
    def __init__(self, name, default=True):
        self.default = default
        dict.__init__(self)
        DumpBaseCls.__init__(self, name)

    def is_show(self, name):
        v = self[name].is_show
        if v == ShowStat.Default:
            return self.default
        else:
            return v == ShowStat.Yes

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.update_to_db()

    def __getitem__(self, key):
        if key not in self:
            self[key] = TableColumn(ShowStat.Default, 80)
        return super().__getitem__(key)

    def set_show(self, name, is_show):
        self[name].is_show = is_show
        self.update_to_db()

    def set_wide(self, name, wide):
        self[name].wide = wide
        self.update_to_db()


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
        self.sql_table = None
        self.dataframe = None

    def setDataFrame(self, dataframe, name:str=None,
                     column_set_cls=ColumnSet, sql_table:SqlTable=None):
        # filter columns
        if name is not None:
            self.column_set = column_table.auto_create(column_set_cls, name)
        elif self.column_set is None:
            raise ValueError('first call setDataFrame without name')
        if sql_table is not None:
            self.sql_table = sql_table
        self.dataframe = dataframe
        data2 = dataframe.copy()
        for col_name in data2.columns:
            if not self.column_set.is_show(col_name):
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
        self.activated.connect(self.active_slot)
        self.pressed.connect(self.pressed_slot)
        headers = self.horizontalHeader()
        headers.sectionResized.connect(self.resized_slot)
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self.horiz_head_right_click)

    def update_dataframe(self):
        self.setDataFrame(self.dataframe)

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
        model = self.model()
        if self.current_edit_widget and self.current_edit_index:  # has other block editing
            widget_old = self.current_edit_widget
            index_old = self.current_edit_index
            column_old = index_old.column()
            name_old = model.headerData(column_old, Qt.Horizontal, role=Qt.DisplayRole)
            value = self.column_set[name_old].on_edit_finish(index_old, widget_old)
            if self.sql_table:
                self.update_sql_table(index_old.row(), name_old, value)
            self.setIndexWidget(index_old, None)
            self.current_edit_widget = None
            self.current_edit_index = None

    def resized_slot(self, i, _, w):
        if not self.column_set:
            return
        col_name = self.model().headerData(i, Qt.Horizontal, role=Qt.DisplayRole)
        self.column_set.set_wide(col_name, w)

    def update_sql_table(self, row: int, col_name: str, value):
        if 'id' not in self.dataframe or not self.sql_table:
            return
        self.dataframe[col_name][row] = value
        xid = self.dataframe['id'][row]
        self.update_dataframe()
        self.sql_table.update_conds({'id': xid}, {col_name: value})

    def horiz_head_right_click(self, point):  # 创建右键菜单
        def Handler():
            self.column_set.set_show(name, False)
            contextMenu.close()
            self.update_dataframe()
            print("已隐藏", name)

        contextMenu = QMenu(self)
        self.hidden = contextMenu.addAction(u'隐藏')
        # self.actionA = self.contextMenu.exec_(self.mapToGlobal(pos))  # 1
        contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        logic_index = self.horizontalHeader().logicalIndexAt(point)
        name = self.model().headerData(logic_index, Qt.Horizontal, role=Qt.DisplayRole)
        self.hidden.triggered.connect(Handler)
        # self.contextMenu.move(self.pos())  # 3
        contextMenu.show()
