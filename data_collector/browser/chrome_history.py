#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:30:43 2020

@author: xrj
"""
import os
from .browser_history import BrowserHistory


class ChromeHistory(BrowserHistory):
    sql = 'SELECT visit_time/1000000-11644473600 FROM visits'
    dbtype = 1002
    coll_name = 'chrome history'

    def __init__(self, source_path=None, plan_name='chrome history'):
        if source_path is None:
            path = os.path.join(os.environ['HOME'], '.config/google-chrome/Default/History')
            if os.path.isfile(path):
                source_path = path
            else:
                raise FileNotFoundError("chrome history file 'History' no found")
            super().__init__(source_path, plan_name)
