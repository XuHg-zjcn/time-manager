import datetime

from PyQt5 import Qsci
from PyQt5.QtWidgets import QColorDialog
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

from Qt_GUI.add_task_gen.dialog import Ui_Dialog
from commd_line.init_config import conf
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
        show = self.show_in2d.checkState() != 0
        style = self.button_color.styleSheet()
        rgb = int(style[-7:-1], base=16)
        tg = TaskGen(name, rec_id, type_id, long,
                     show, rgb, cron, start, stop)
        return tg

    def set_tg(self, tg: TaskGen):
        self.start.setDateTime(datetime.datetime.fromtimestamp(tg.start_time))
        self.stop.setDateTime(datetime.datetime.fromtimestamp(tg.stop_time))
        self.cron_text.setText(tg.expr)
        # ', ' can't pass check, raise Error below:
        # ValueError: multiply unused char continuous
        long_str = str(datetime.timedelta(seconds=tg.long)).replace(',', '')
        self.long_text.setText(long_str)
        self.recid_spin.setValue(tg.db_fields['rec_id'])
        self.typeid_spin.setValue(tg.db_fields['type_id'])
        self.show_in2d.setCheckState(tg.db_fields['show']*2)
        rgb = tg.db_fields['color']
        self.button_color.setStyleSheet(f'QWidget {{background-color:#{rgb:06x}}}')

    def show_job_code(self, name):
        with open(f'./code/{name}.py', 'r') as f:
            text = f.read()
        self.editor.setText(text)

    def add_job(self, name, tg):
        sched = BackgroundScheduler()
        url = 'sqlite:///' + conf['init']['db_path']
        sched.add_jobstore('sqlalchemy', url=url)
        # save user's code to .py file
        text = self.editor.text()
        with open(f'./code/{name}.py', 'w') as f:
            f.write(text)
        # cron expr as dict
        expr = tg._expr_format.split(' ')
        fields = ['minute', 'hour', 'day', 'month', 'day_of_week', 'second']
        kwargs = dict(zip(fields, expr))
        # add user's custom scheduler_job
        sched.start()  # save job to sqlite
        try:
            sched.remove_job(name)
        except JobLookupError:
            pass
        exec(f'from user_data.code.{name} import scheduler_job\n'
             "sched.add_job(scheduler_job, 'cron', id=name, **kwargs)")
        sched.shutdown()

    @staticmethod
    def remove_job(name):
        sched = BackgroundScheduler()
        url = 'sqlite:///' + conf['init']['db_path']
        sched.add_jobstore('sqlalchemy', url=url)
        sched.start()
        sched.remove_job(name)
        sched.shutdown()

    def add_db_slot(self, b):
        tg = self.get_tg()
        name = tg.db_fields['name']
        is_add = tg_tab.name_auto_insert_or_update(tg, True)
        if is_add:
            self.name_comb.addItem(name)
        self.add_job(name, tg)

    def delete_slot(self, b):
        name = self.name_comb.currentText()
        tg_tab.delete({'name': name}, True)
        self.remove_job(name)
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
        self.show_job_code(text)

    def show_in2d_slot(self, b):
        name = self.name_comb.currentText()
        b = b != 0
        if b and name not in self.parent.dt2d_plot.items:
            tg = self.get_tg()
            ivt = tg.get_ivtree()
            rgb = tg.db_fields['color']
            self.parent.dt2d_plot.draw_ivtree(ivt, default_color=rgb, name=name)
            tg_tab.update_conds({'name': name}, {'show': b})
        if not b and name in self.parent.dt2d_plot.items:
            self.parent.dt2d_plot.remove_plans(name)
            tg_tab.update_conds({'name': name}, {'show': b})

    def show_in2d_init(self):
        tgs = tg_tab.get_conds_objs({'show': 1})  # select showing TaskGen
        for tg in tgs:
            ivt = tg.get_ivtree()
            name = tg.db_fields['name']
            rgb = tg.db_fields['color']
            self.parent.dt2d_plot.draw_ivtree(ivt, default_color=rgb, name=name)

    def combo_init(self):
        texts = tg_tab.get_conds_execute(fields='name')
        self.name_comb.addItems(texts)

    def button_color_slot(self, b):
        name = self.name_comb.currentText()
        col = QColorDialog.getColor()
        rgb = col.rgb() % 0x01000000
        tg_tab.update_conds({'name': name}, {'color': rgb}, commit=True)
        self.button_color.setStyleSheet(f'QWidget {{background-color:{col.name()}}}')
        if name in self.parent.dt2d_plot.items:
            self.parent.dt2d_plot.remove_plans(name)
            self.show_in2d_slot(True)

    def build(self):
        self.button_color.setStyleSheet('QWidget {background-color:#00ffff}')
        self.name_comb.currentTextChanged.connect(self.combo_text_change_slot)
        self.add_to_db.clicked.connect(self.add_db_slot)
        self.delete_db.clicked.connect(self.delete_slot)
        self.list_out_tasks.clicked.connect(self.list_out_tasks_slot)
        self.remove_tasks.clicked.connect(self.remove_tasks_slot)
        self.show_in2d.stateChanged.connect(self.show_in2d_slot)
        lexer = Qsci.QsciLexerPython(self.editor)
        self.editor.setLexer(lexer)
        with open('../my_libs/default_job.py') as f:
            default_code = f.read()
        self.editor.setText(default_code)
        self.combo_init()
        self.show_in2d_init()
        self.button_color.clicked.connect(self.button_color_slot)
