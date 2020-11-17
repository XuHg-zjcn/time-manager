#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:30:43 2020

@author: xrj
"""

from browser_history import browser_history

browser_db_path = 'History'
my_db_path = 'chrome_history.db'
sql = 'SELECT visit_time/1000000-11644473600 FROM visits'

browser_history(browser_db_path, my_db_path, sql, 'chrome', 2)
