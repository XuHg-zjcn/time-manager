#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 13:32:38 2020

@author: xrj
"""
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from time_str import Time_str

test_str = '28/Oct 12:34:56.123'
graphviz = GraphvizOutput()
graphviz.output_file = 'graph.png'
with PyCallGraph(output=graphviz):
    tstr = Time_str(test_str)
    datetime = tstr.as_datetime()
