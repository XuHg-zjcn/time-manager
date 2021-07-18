#!/bin/python
from commd_line.init_config import conn
from my_libs.sqltable import SqlTable

class TimePoints_db(SqlTable):
    """
    用于保存时间点数据
    """
    name2dtype = [('rec_id', 'INT'),
                  ('type_id', 'INT'),
                  ('num', 'NUMERIC'),
                  ('time', 'REAL'),
                  ('desc', 'TEXT')]
    table_name = 'timepoints_data'

tpd = TimePoints_db(conn)
