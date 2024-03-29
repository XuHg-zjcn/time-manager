#!/bin/python
import os

from git import Repo

from sqlite_api.timepoint_db import tpd
from .auto_collect import Collector

class GitLog(Collector):
    def __init__(self):
        self.path = input('请输入路径')
        self.name = os.path.split(self.path)[-1]

    def run(self):
        repo = Repo(self.path)
        logs = repo.head.log()
        t_min = float('inf')
        t_max = float('-inf')
        items = 0
        for log in logs:
            lst = list(tpd.get_conds_execute({'rec_id':self.db_fields['id'], 'num':log.newhexsha}))
            if lst:
                continue
            spt = log.message.find(':')
            if spt < 0:
                spt = 0
            tpd.insert({'rec_id':self.db_fields['id'],
                        'type_id':log.message[:spt],
                        'num':log.newhexsha,
                        'time':log.time[0],
                        'desc':log.message[spt+1:]})
            items += 1
            if log.time[0] < t_min:
                t_min = log.time[0]
            if log.time[0] > t_max:
                t_max = log.time[0]
        if items == 0:
            t_min = t_max = None
        return t_min, t_max, items
