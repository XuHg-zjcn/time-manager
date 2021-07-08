from my_libs.sqltable import SqlTable
from .add_plot import Ui_Dialog
import user_data.code.addplot_ops as ops1
import Qt_GUI.addplot_ops as ops2
from commd_line.init_config import conn

class PlotTable(SqlTable):
    name2dtype = [('name', 'TEXT'), ('func', 'TEXT'), ('param', 'TEXT'), ('color', 'INT')]
    table_name = 'plot_table'

ptab = PlotTable(conn)

# TODO: apply button, run func
class AddPlot2(Ui_Dialog):
    def build(self):
        self.buttonBox.accepted.connect(lambda : self.on_accepted())
        self.combo_name.editTextChanged.connect(self.on_name_change)
        self.combo_func.editTextChanged.connect(self.on_func_change)
        self.load_all_names()
        self.load_all_funcs()

    def on_accepted(self):
        name = self.combo_name.currentText()
        func = self.combo_func.currentText()
        param = self.combo_param.currentText()
        color = self.lineEdit_color.text()
        color = int(color, base=16)
        iid = ptab.get_conds_onlyone({'name':name}, 'id', def0=None)
        if iid is None:
            ptab.insert({'name': name, 'func': func, 'param': param, 'color': color}, commit=True)
        else:
            ptab.update_conds({'id': iid}, {'func': func, 'param': param, 'color': color}, commit=True)

    def on_func_change(self):
        func = self.combo_func.currentText()
        ptab.get_conds_execute({'func': func}, ['name', 'param'])

    def on_name_change(self, s):
        print(s)
        if self.combo_name.findText(s) == -1:
            self.load_all_funcs()
        else:
            func, param, color = ptab.get_conds_onlyone({'name':s}, ['func', 'param', 'color'])
            self.combo_func.setEditText(func)
            self.combo_param.setEditText(param)
            self.lineEdit_color.setText(hex(color))

    def load_all_names(self):
        names = ptab.get_conds_execute(None, 'name')
        self.combo_name.clear()
        self.combo_name.addItems(names)

    def load_all_funcs(self):
        dops1 = dir(ops1)
        dops1 = filter(lambda x:x[:2] != '__' and callable(getattr(ops1, x)), dops1)
        dops1 = list(dops1)
        dops2 = dir(ops2)
        dops2 = filter(lambda x:x[:2] != '__' and callable(getattr(ops2, x)), dops2)
        dops2 = list(dops2)
        dops = dops1 + dops2
        self.combo_func.clear()
        self.combo_func.addItems(dops)
