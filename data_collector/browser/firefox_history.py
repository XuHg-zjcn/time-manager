#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 02:17:41 2020

@author: xrj
"""
import os
import glob
from .browser_history import BrowserHistory


sql = 'SELECT visit_date/1000000 FROM moz_historyvisits'

class FirefoxHistory(BrowserHistory):
    sql = 'SELECT visit_date/1000000 FROM moz_historyvisits'
    dbtype = 1001
    coll_name = 'firefox history'

    def __init__(self, source_path=None, plan_name='firefox history'):
        if source_path is None:
            paths = glob.glob(os.path.join(os.environ['HOME'], '.mozilla/firefox/*.default-release/places.sqlite'))
            if len(paths) == 0:
                raise FileNotFoundError("firefox history file 'places.sqlite' no found")
            elif len(paths) == 1:
                source_path = paths[0]
            else:
                inp = input('请选择:' + '\n'.join(paths) + '\n')
                source_path = paths[int(inp)]
        super().__init__(source_path, plan_name)
