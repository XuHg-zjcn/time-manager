#!/bin/python
from .wtmp import wtmp_iter
from sqlite_api.collect_data import cdt
from commd_line.init_config import conn

# TODO: save collector obj in CollTable
for sta, end, xtype in wtmp_iter():
    print(sta, end, xtype)
    try:
        cdt.insert({'rec_id':12345, 'type_id':0, 'sta':sta, 'end':end, 'num':xtype})
    except ValueError as e:
        print(e)
cdt.commit()
conn.close()
print(cdt.conn)
