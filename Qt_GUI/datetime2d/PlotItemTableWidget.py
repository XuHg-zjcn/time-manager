from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtWidgets import QMenu
from Qt_GUI.datetime2d.DictTableWidget import DictTableWidget


class PlotItemTableWidget(DictTableWidget):
    dele = pyqtSignal(str)
    addreq = pyqtSignal()
    """
    show plot items in table widget
    """
    def build(self):
        self.setHorizontalHeaderLabels(['类型', '名称', '子条目', '其他'])
        self.setHorizontalScrollBarPolicy
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)

    # TODO: 应该在行头弹出
    def generateMenu(self, pos):
        # print(pos)
        menu = QMenu()
        indexes = self.selectedIndexes()
        if len(indexes) == 0:
            item = menu.addAction(u"添加")
            item.triggered.connect(self.addreq.emit)
        else:
            rows = set()
            for i in indexes:
                rows.add(i.row())
            if len(rows) != 1:   
                raise ValueError('multiply select')
            else:
                row = rows.pop()
            item = menu.addAction(u"删除")
            name = self.item(row, 1).data(0)
            item.triggered.connect(lambda x: self.dele.emit(name))
        action = menu.exec_(self.mapToGlobal(pos))
