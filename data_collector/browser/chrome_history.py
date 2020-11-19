#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:30:43 2020

@author: xrj
"""
from browser_history import browser_history
import sys
sys.path.append('../../')
from commd_line.init_config import init_config

conf = init_config()
browser_db_path = 'History'
my_db_path = 'browser.db'
sql = 'SELECT visit_time/1000000-11644473600 FROM visits'

browser_history(browser_db_path, my_db_path, sql,
                table_name='chrome', plan_name='visit', plan_dbtype=2)
