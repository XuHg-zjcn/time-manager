#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# run the file in background, timer
from apscheduler.schedulers.blocking import BlockingScheduler

from commd_line.init_config import conf
from sqlite_api.task_gen import tg_tab

if __name__ == '__main__':
    tgs = tg_tab.get_conds_objs(None)
    sched = BlockingScheduler()
    url = 'sqlite:///' + conf['init']['db_path']
    sched.add_jobstore('sqlalchemy', url=url)
    sched.start()
