import os
import threading
from sqlite_api import sqlite_api
from time_algh import event
from net_mgr import net_mgr

if __name__=='__main__':
    sql_db = sqlite_api('net_mgr.db')
    net = net_mgr()
    while True:
        dt = net.on()
        sql_db.update(event(dt, True))
        inp = input('已连接，按回车断网:')
        dt = net.off()
        sql_db.update(event(dt, False))
        inp = input('已断开，按回车连网，输入exit或q退出:')
        if(inp in {'exit', 'q'}):
            break

