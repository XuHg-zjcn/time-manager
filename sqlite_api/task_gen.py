from croniter import croniter

from my_libs.dump_table import DumpTable, DumpBaseCls
from sqlite_api.task_db import Plan, TaskTable


class CronPointGen(croniter):
    def __init__(self, expr_format, start_time=None, stop_time=None, max_step=1000):
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


class TaskGen(CronPointGen, DumpBaseCls):
    names_autoload = {'id', 'table', 'name', 'rec_id', 'type_id'}

    def __init__(self, name='tg', rec_id=-1, type_id=-1,
                 long=3600.0, *args, **kwargs):
        CronPointGen.__init__(self, *args, **kwargs)
        DumpBaseCls.__init__(self, name)
        self.db_fields['rec_id'] = rec_id
        self.db_fields['type_id'] = type_id
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


class TaskGenTable(DumpTable):
    name2dtype = [('name', 'TEXT'),
                  ('dump', 'BLOB'),
                  ('runs', 'INT'),
                  ('rec_id', 'INT'),
                  ('type_id', 'INT')]
    table_name = 'task_gen_table'
