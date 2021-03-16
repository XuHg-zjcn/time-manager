# most copy from https://blog.csdn.net/weixin_40530134/article/details/95031370

from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu

from Qt_GUI.tabview import TableViewWithColumnSet, ColumnSet
from my_libs.sqltable import SqlTable


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


class iTableView(TableViewWithColumnSet):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataframe = None

    def setDataFrame(self, dataframe, name: str=None,
                     column_set_cls=ColumnSet, sql_table:SqlTable=None):
        # filter columns
        if name is not None:
            self.SetColumnSet(name, column_set_cls)
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
        self.init_wides()
        # connect signals, TODO: edit in TabView, write to database.

    def update_dataframe(self):
        self.setDataFrame(self.dataframe)

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
