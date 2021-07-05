from my_libs.sqltable import SqlTable
from .add_plot import Ui_Dialog
import user_data.code.addplot_ops as ops

class PlotTable(SqlTable):
    name2dtype = [('name', 'TEXT'), ('func', 'TEXT'), ('param', 'TEXT'), ('color', 'INT')]
    table_name = 'table_name'


class AddPlot2(Ui_Dialog):
    def build(self):
        self.buttonBox.accepted.connect(lambda : self.on_accepted())
        dops = dir(ops)
        dops = filter(lambda x:x[:2]!='__' and callable(getattr(ops, x)), dops)
        dops = list(dops)
        self.combo_func.addItems(dops)

    def on_accepted(self):
        name = self.combo_name.currentText()
        func = self.combo_func.currentText()
        param = self.combo_param.currentText()
        color = self.lineEdit_color.text()
        print(name, func, param, color)
