#!/bin/python
import utmp
from sqlite_api.collect_data import cdt
from commd_line.init_config import conn

t_sta = None

# TODO: save collector obj in CollTable
with open('/var/log/wtmp', 'rb') as fd:
    buf = fd.read()
    for entry in utmp.read(buf):
        if entry.user == 'runlevel':
            t_sta = entry.sec + entry.usec/1e6
        elif entry.user == 'shutdown' and t_sta is not None:
            t_end = entry.sec + entry.usec/1e6
            cdt.insert({'rec_id':12345, 'type_id':0, 'sta':t_sta, 'end':t_end, 'num':0})
cdt.commit()
conn.close()
print(cdt.conn)
