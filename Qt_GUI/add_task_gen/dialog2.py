import datetime

from Qt_GUI.add_task_gen.dialog import Ui_Dialog
from commd_line.init_config import conn
from my_libs.sqltable import onlyone_process
from sqlite_api.task_db import TaskTable
from sqlite_api.task_gen import TaskGenTable, TaskGen

tg_tab = TaskGenTable(conn)
task_tab = TaskTable(conn)


# TODO: 3 spin box as a widget, direct get range obj.
class AddTaskGenDialog(Ui_Dialog):
    def get_tg(self):
        year = range(self.year_min.value(), self.year_max.value(), self.year_period.value())
        mon = range(self.mon_min.value(), self.mon_max.value(), self.mon_period.value())
        day = range(self.day_min.value(), self.day_max.value(), self.day_period.value())
        week = range(self.week_min.value(), self.week_max.value(), self.week_period.value())
        hour = range(self.hour_min.value(), self.hour_max.value(), self.hour_period.value())
        minu = range(self.minu_min.value(), self.minu_max.value(), self.minu_period.value())
        sec = range(self.sec_min.value(), self.sec_max.value(), self.sec_period.value())
        long = datetime.timedelta(days=self.day_long.value(),
                                  hours=self.hour_long.value(),
                                  minutes=self.minu_long.value(),
                                  seconds=self.sec_long.value()).total_seconds()
        name = self.name_comb.currentText()
        rec_id = self.recid_spin.value()
        type_id = self.typeid_spin.value()
        tg = TaskGen(name, rec_id, type_id, long,
                     year, mon, day, week, hour, minu, sec)
        return tg

    def set_tg(self, tg: TaskGen):
        year, mon, day, hour, minu, sec = tg.groups
        week = tg.week
        long = tg.long
        self.year_min.setValue(year.start)
        self.year_max.setValue(year.stop)
        self.year_period.setValue(year.step)
        self.mon_min.setValue(mon.start)
        self.mon_max.setValue(mon.stop)
        self.mon_period.setValue(mon.step)
        self.day_min.setValue(day.start)
        self.day_max.setValue(day.stop)
        self.day_period.setValue(day.step)
        self.hour_min.setValue(hour.start)
        self.hour_max.setValue(hour.stop)
        self.hour_period.setValue(hour.step)
        self.minu_min.setValue(minu.start)
        self.minu_max.setValue(minu.stop)
        self.minu_period.setValue(minu.step)
        self.sec_min.setValue(sec.start)
        self.sec_max.setValue(sec.stop)
        self.sec_period.setValue(sec.step)
        self.week_min.setValue(week.start)
        self.week_max.setValue(week.stop)
        self.week_period.setValue(week.step)
        self.day_long.setValue(long//86400); long%=86400
        self.hour_long.setValue(long//3600); long%=3600
        self.minu_long.setValue(long//60); long%=60
        self.sec_long.setValue(long)

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

    def combo_init(self):
        texts = tg_tab.get_conds_execute(fields='name')
        self.name_comb.addItems(texts)

    def build(self):
        self.name_comb.currentTextChanged.connect(self.combo_text_change_slot)
        self.add_to_db.clicked.connect(self.add_db_slot)
        self.delete_db.clicked.connect(self.delete_slot)
        self.list_out_tasks.clicked.connect(self.list_out_tasks_slot)
        self.remove_tasks.clicked.connect(self.remove_tasks_slot)
        self.combo_init()
