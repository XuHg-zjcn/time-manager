#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 02:17:41 2020

@author: xrj
"""
from browser_history import browser_history
from commd_line.init_config import init_config
import argparse

conf = init_config()
my_db_path = conf['init']['db_path']

parser = argparse.ArgumentParser()
parser.add_argument("--table_name", required=True)
parser.add_argument("--dbtype", required=True)
parser.add_argument("--source_path", required=True)
args = parser.parse_args()

sql = 'SELECT visit_date/1000000 FROM moz_historyvisits'

browser_history(args.source_path,
                my_db_path, sql,
                table_name=args.table_name,
                plan_name='firefox visit',
                plan_dbtype=args.dbtype)
