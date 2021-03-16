from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSpinBox, QTableView, QWidget

from commd_line.init_config import conn
from my_libs.dump_table import DumpBaseCls, DumpTable


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


class TableViewWithColumnSet(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_set = None
        self.sql_table = None
        self.current_edit_index = None
        self.current_edit_widget = None
        self.activated.connect(self.active_slot)
        self.pressed.connect(self.pressed_slot)
        headers = self.horizontalHeader()
        headers.sectionResized.connect(self.resized_slot)
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self.horiz_head_right_click)

    def SetColumnSet(self, name, column_set_cls=None):
        """
        find or create ColumnSet in sqlite table 'column_set_table'

        @param name: name in column_table
        @param column_set_cls: if can't find in column_table, auto create
        @return: None
        """
        if name is not None:
            self.column_set = column_table.auto_create(name, column_set_cls)
        elif self.column_set is None:
            raise ValueError('column set not found')

    def on_builds(self):
        """
        call on_build function in ColumnSet for each table cell.

        @return: None
        """
        if self.column_set is None:
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

    def init_wides(self):
        """
        load column wides in ColumnSet.

        @return: None
        """
        if not self.column_set:
            return
        model = self.model()
        i2name = map(lambda x:model.headerData(x, Qt.Horizontal, role=Qt.DisplayRole),
                     range(model.columnCount()))
        for i, col_name in enumerate(i2name):
            self.setColumnWidth(i, self.column_set[col_name].wide)

    def active_slot(self, qmi):
        """
        Qt signal slot, double click slot, edit this cell.

        @param qmi: QModelIndex of cell
        @return: None
        """
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
        """
        Qt signal slot, single click, finish current editing cell(maybe isn't `qmi`).

        @param qmi: QModelIndex of cell, unused
        @return: None
        """
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
