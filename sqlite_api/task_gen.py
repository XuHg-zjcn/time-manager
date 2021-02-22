from croniter import croniter
import pandas as pd

from commd_line.init_config import conn
from my_libs.dump_table import DumpTable, DumpBaseCls
from sqlite_api.task_db import Plan, TaskTable, Plans


class CronPointGen(croniter):
    def __init__(self, expr_format, start_time=None, stop_time=None, max_step=1000):
        """
        croniter with stop_time and max_step.

        @param expr_format: Quartz cron time expression
        @param start_time: datetime or unix timestamp
        @param stop_time: unix timestamp, max time of iter
        @param max_step: integer, max step of iter
        """
        e = expr_format.split(' ')  # '(sec) minu hour day mon week'
        if len(e) == 6:
            e.append(e.pop(0))      # move second to last
            expr_format = ' '.join(e)
        super().__init__(expr_format, start_time)
        self.stop_time = stop_time
        self.max_step = max_step
        self.count = 0

    def __next__(self):
        ret = super().__next__()
        self.count += 1
        if ret > self.stop_time or self.count > self.max_step:
            raise StopIteration
        return ret

    @property
    def expr(self):
        expr = self._expr_format   # 'minu hour day mon week (sec)'
        e = expr.split(' ')
        if len(e) == 6:
            e.insert(0, e.pop(5))  # move second to first
            expr = ' '.join(e)
        return expr


class TaskGen(CronPointGen, DumpBaseCls):
    names_autoload = {'id', 'table', 'name', 'rec_id', 'type_id', 'show'}

    def __init__(self, name='tg', rec_id=-1, type_id=-1,
                 long=3600.0, show=True, *args, **kwargs):
        CronPointGen.__init__(self, *args, **kwargs)
        DumpBaseCls.__init__(self, name)
        self.db_fields['rec_id'] = rec_id
        self.db_fields['type_id'] = type_id
        self.db_fields['show'] = show
        self.long = long

    def __next__(self):
        sta = CronPointGen.__next__(self)
        end = sta + self.long
        d = {'rec_id': self.db_fields['rec_id'],
             'type_id': self.db_fields['type_id'],
             'name': self.db_fields['name'],
             'sta': sta,
             'end': end,
             'num': self.count}
        return Plan(d)

    def add_to_task_table(self, task_table: TaskTable):
        for p in self:
            df = task_table.get_conds_plans({'rec_id': p['rec_id'], 'num': p['num']})
            if len(df) == 0:
                task_table.insert(p, commit=False)
        if not task_table.commit_each:
            task_table.commit()

    def get_plans(self):
        return Plans(pd.DataFrame(self))


class TaskGenTable(DumpTable):
    name2dtype = [('name', 'TEXT'),
                  ('dump', 'BLOB'),
                  ('runs', 'INT'),
                  ('rec_id', 'INT'),
                  ('type_id', 'INT'),
                  ('show', 'BOOL')]
    table_name = 'task_gen_table'


tg_tab = TaskGenTable(conn)
