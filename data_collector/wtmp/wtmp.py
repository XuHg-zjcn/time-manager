#!/bin/python
from wtmp.build import libwtmp_cpp as wtmp

class wtmp_iter:
    def __iter__(self):
        return self

    def __next__(self):
        sta, end, xtype = wtmp.next()
        if xtype == -1:
            raise StopIteration
        return sta, end, xtype

if __name__ == '__main__':
    for sta, end, xtype in wtmp_iter():
        print(sta, end, xtype)
