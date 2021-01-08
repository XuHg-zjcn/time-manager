from PyQt5.QtWidgets import QTableWidgetItem


def test(tw):
    tw.setRowCount(3)
    tw.setColumnCount(3)
    tw.setHorizontalHeaderLabels(['a', 'b', 'c'])
    tw.setVerticalHeaderLabels(['1', '2', '3'])
    for row in range(3):
        for column in range(3):
            item = QTableWidgetItem('row %s,column %s' % (row, column))
            tw.setItem(row, column, item)
