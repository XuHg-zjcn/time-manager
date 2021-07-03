from commd_line.init_config import conn
from my_libs.sqltable import SqlTable


class CollDataTable(SqlTable):
    """
    用于保存自动收集的数据
    """
    name2dtype = [('rec_id', 'INT'),
                  ('type_id', 'INT'),
                  ('num', 'NUMERIC'),
                  ('sta', 'REAL'),
                  ('end', 'REAL'),
                  ('state', 'INT')]
    table_name = 'coll_data'

cdt = CollDataTable(conn)
