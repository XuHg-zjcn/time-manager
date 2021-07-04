from collections import namedtuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


Item = namedtuple('Item', ['sType', 'obj'])  # name save in Dict keys


# don't use dict as base class, else raise this error:
# TypeError: multiple bases have instance lay-out conflict
class DictTableWidget(QTableWidget):
    """
    QTableWidget with dict(self.Dict)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Dict = {}

    def __setitem__(self, name, obj):
        """
        add item to TableWidget, and save to dict.
        @param name: name of item, `None` for default item
        @param obj: item object, can get by __getitem__
        """
        sType = obj.__class__.__name__
        if name in self.Dict:             # key already exists
            row = self.Dict[name].row
        else:                            # key not exists
            row = len(self.Dict)
            self.Dict.__setitem__(name, Item(sType, obj))
            self.setRowCount(row+1)
        self.setItem(row, 0, QTableWidgetItem(sType))
        self.setItem(row, 1, QTableWidgetItem(str(name)))

    def __getitem__(self, name):
        """
        hidden other info, only return same value in __setitem__
        @param name: name of item
        @return: item object
        """
        return self.Dict[name].obj

    def __contains__(self, name):
        return self.Dict.__contains__(name)

    def pop(self, name):
        """
        remove item in TableWidget and pop it in dict
        @param name: name of item
        @return: item object pop by dict
        """
        row = self.findItems(name, Qt.MatchExactly)[0].row()
        self.removeRow(row)
        print('removeRow', row)
        return self.Dict.pop(name).obj

    def values(self):
        """
        iter items
        @return: map object
        """
        return map(lambda x: x.obj, self.Dict.values())

    def clear(self):
        """
        clear Dict, not clear QTableWidget
        """
        self.Dict.clear()

    def __getattr__(self, item):
        """
        getattr in self.Dict
        @param item: attr name
        """
        if hasattr(self.Dict, item):
            return getattr(self.Dict, item)
        else:
            raise AttributeError("'QTableWidget' and 'dict' are not has"
                                 f"attribute '{item}'")
