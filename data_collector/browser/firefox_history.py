"""
Created on Tue Nov 17 02:17:41 2020

@author: xrj
"""
import os
import glob
from .browser_history import BrowserHistory


class FirefoxHistory(BrowserHistory):
    sql = 'SELECT visit_date/1000000 FROM moz_historyvisits'
    coll_name = 'firefox history'
    plan_name = 'firefox visit'

    def __init__(self, source_path=None, plan_name=plan_name):
        if source_path is None:
            paths = glob.glob(os.path.join(os.environ['HOME'], '.mozilla/firefox/*.default-release/places.sqlite'))
            if len(paths) == 0:
                raise FileNotFoundError("firefox history file 'places.sqlite' no found")
            elif len(paths) == 1:
                source_path = paths[0]
            else:
                inp = input('请选择:' + '\n'.join(paths) + '\n')
                source_path = paths[int(inp)]
        super().__init__(source_path, plan_name)
