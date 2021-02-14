from datetime import datetime
from collections import Iterable, Container

from my_libs.dump_table import DumpTable, DumpBaseCls
from sqlite_api.task_db import Plan, TaskTable
from commd_line.init_config import conn


class UpBit(Exception):
    pass  # up bigger iterators, and reinit smaller iterators


class MyStop(Exception):
    pass  # end of iter SeqGen


skip = object()  # flag of skip the current result, can return in SeqGen.test


class SeqGen:
    def __init__(self, groups, chks=None):
        self.groups = list(map(lambda x: x if isinstance(x, Iterable) else (x,), groups))
        assert len(self.groups) >= 1, 'groups length must >=1'
        self.states = list(map(iter, self.groups))
        self.last_s = list(map(next, self.states[:-1])) + [None]  # don't call last iter
        if chks is None:
            chks = []
        self.chks = chks
        self.count = 0

    def test(self):
        try:
            for chk in self.chks:
                chk(self.last_s)
        except Exception:
            return skip

    def clears(self, index):
        """
        reset >index iterators
        """
        if index < 0:
            index = len(self.groups) + index
        for i in range(index, len(self.groups)):    # reset iterators
            self.states[i] = iter(self.groups[i])
            self.last_s[i] = next(self.states[i])

    def next(self, index=-1):
        if index < -len(self.states):
            raise MyStop                            # negative index over head
        try:
            self.last_s[index] = next(self.states[index])
            while True:
                if self.test() is not skip:
                    break
                self.next()
        except (StopIteration, UpBit):
            assert index != 0, 'index over head'
            self.clears(index)  # notice: clear all before raise MyStop, the state will not keep.
            self.next(index-1)
        else:
            self.count += 1
            return self.last_s

    def proc(self):
        return self.last_s

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self.next()
        except MyStop:
            raise StopIteration
        return self.proc()


class DatetimePointGen(SeqGen):
    def __init__(self, year=range(2000, 2100),
                 mon=range(1, 13), day=range(1, 32), week=None,
                 hour=0, minu=0, sec=0):
        groups = [year, mon, day, hour, minu, sec]
        super().__init__(groups)
        if isinstance(week, Container) or week is None:
            pass
        if isinstance(week, int):
            week = (week,)
        self.week = week

    def test(self):
        try:
            dt = datetime(*self.last_s)
        except ValueError as e:
            raise UpBit(e)
        if self.week is not None:
            if dt.weekday() not in self.week:
                return skip

    def proc(self):
        return datetime(*self.last_s)


class TaskGen(DatetimePointGen, DumpBaseCls):
    def __init__(self, name='tg', rec_id=-1, type_id=-1,
                 long=3600, *args, **kwargs):
        DatetimePointGen.__init__(*args, **kwargs)
        DumpBaseCls.__init__(self, name)
        self.db_fields['rec_id'] = rec_id
        self.db_fields['type_id'] = type_id
        self.long = long

    def proc(self):
        sta = super().proc().timestamp()
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


if __name__ == '__main__':
    tg_tab = TaskGenTable(conn)
    task_tab = TaskTable(conn)
    dtg = TaskGen(year=range(2020, 2030),
                  mon=range(1, 3), day=range(1, 3),
                  rec_id=4, type_id=2, name='task_gen2')

    tg_tab.add_obj(dtg)
    dtg = tg_tab.get_conds_objs({'name': 'TaskGen'})[0]
    dtg.add_to_task_table(task_tab)
    for i in dtg:
        print(i)
