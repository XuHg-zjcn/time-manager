import datetime

from Qt_GUI.add_task_gen.dialog import Ui_Dialog
from my_libs.smart_strptime import TimeDelta_str
from my_libs.sqltable import onlyone_process
from sqlite_api.task_db import task_tab
from sqlite_api.task_gen import TaskGen, tg_tab


# TODO: 3 spin box as a widget, direct get range obj.
class AddTaskGenDialog(Ui_Dialog):
    def __init__(self, parent):
        self.parent = parent

    def get_tg(self):
        start = self.start.dateTime().toTime_t()
        stop = self.stop.dateTime().toTime_t()
        cron = self.cron_text.text()
        long_text = self.long_text.text()
        td_str = TimeDelta_str(long_text)
        td_str.process_check()
        long = td_str.as_sec()
        name = self.name_comb.currentText()
        rec_id = self.recid_spin.value()
        type_id = self.typeid_spin.value()
        tg = TaskGen(name, rec_id, type_id, long, cron, start, stop)
        return tg

    def set_tg(self, tg: TaskGen):
        self.start.setDateTime(datetime.datetime.fromtimestamp(tg.start_time))
        self.stop.setDateTime(datetime.datetime.fromtimestamp(tg.stop_time))
        self.cron_text.setText(tg._expr_format)
        # ', ' can't pass check, raise Error below:
        # ValueError: multiply unused char continuous
        long_str = str(datetime.timedelta(seconds=tg.long)).replace(',', '')
        self.long_text.setText(long_str)
        self.recid_spin.setValue(tg.db_fields['rec_id'])
        self.typeid_spin.setValue(tg.db_fields['type_id'])

    def add_db_slot(self, b):
        tg = self.get_tg()
        name = tg.db_fields['name']
        is_add = tg_tab.name_auto_insert_or_update(tg, True)
        if is_add:
            self.name_comb.addItem(name)

    def delete_slot(self, b):
        name = self.name_comb.currentText()
        tg_tab.delete({'name': name}, True)
        self.name_comb.removeItem(self.name_comb.currentIndex())

    def list_out_tasks_slot(self, b):
        tg = self.get_tg()
        tg.add_to_task_table(task_tab)

    def remove_tasks_slot(self, b):
        name = self.name_comb.currentText()
        task_tab.delete({'name': name}, True)

    def combo_text_change_slot(self, text):
        tg = onlyone_process(tg_tab.get_conds_objs({'name': text}), def0=None)
        if tg is None:
            return
        self.set_tg(tg)

    def preview_slot(self, b):
        tg = self.get_tg()
        ivtree = tg.get_plans()
        self.parent.dt2d_plot.draw_plans(ivtree, name='preview')

    def combo_init(self):
        texts = tg_tab.get_conds_execute(fields='name')
        self.name_comb.addItems(texts)

    def build(self):
        self.name_comb.currentTextChanged.connect(self.combo_text_change_slot)
        self.add_to_db.clicked.connect(self.add_db_slot)
        self.delete_db.clicked.connect(self.delete_slot)
        self.list_out_tasks.clicked.connect(self.list_out_tasks_slot)
        self.remove_tasks.clicked.connect(self.remove_tasks_slot)
        self.preview.clicked.connect(self.preview_slot)
        self.combo_init()
