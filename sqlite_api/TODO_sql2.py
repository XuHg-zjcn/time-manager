#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 16:26:44 2020

@author: xrj
"""


sql_create = '''CREATE TABLE todo(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type     INT,
    name     TEXT,  desc     TEXT,  remark   TEXT,  comment  TEXT,
    pares    BLOB,  subs     BLOB,  reqs     BLOB,
    sta_time REAL,  end_time REAL,  use_time REAL,  sub_time REAL,
    sta_err  REAL,  end_err  REAL,  use_err  REAL,  sub_err  REAL,
    sta_act  REAL,  end_act  REAL,  use_act  REAL,  sub_act  REAL,
   late_loss REAL, leave_loss REAL, cancal_loss REAL,
    status    INT,  score    REAL);'''
sql_insert = "INSERT INTO todo VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
?,?,?,?,?,?,?,?);"