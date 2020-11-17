#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 02:17:41 2020

@author: xrj
"""

from browser_history import browser_history

browser_db_path = 'places.sqlite'
my_db_path = 'firefox_history.db'
sql = 'SELECT visit_date/1000000 FROM moz_historyvisits'

browser_history(browser_db_path, my_db_path, sql, 'firefox', 1)
