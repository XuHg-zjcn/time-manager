#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 13:32:38 2020

@author: xrj
"""
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from time_str import Time_str
import os

def get_new_fn():
    lsdir = os.listdir('graphs')
    num = 1
    for fn in lsdir:
        if fn[-4:] == '.png':
            i = int(fn[:-4])
            if i > num:
                num = i
    return 'graphs/{}.png'.format(num+1)

test_str = '28/Oct 12:34:56.123'
graphviz = GraphvizOutput()
filename = get_new_fn() #graphs/x.png
graphviz.output_file = filename
with PyCallGraph(output=graphviz):
    tstr = Time_str(test_str)
    tstr.process_check()
print('graph save in {}'.format(filename))
