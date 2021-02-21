"""
Created on Tue Nov 17 14:30:43 2020

@author: xrj
"""
import os
from .browser_history import BrowserHistory


class ChromeHistory(BrowserHistory):
    sql = 'SELECT visit_time/1000000-11644473600 FROM visits'
    name = 'chrome history'

    def __init__(self, name=name, source_path=None):
        if source_path is None:
            path = os.path.join(os.environ['HOME'], '.config/google-chrome/Default/History')
            if os.path.isfile(path):
                source_path = path
            else:
                raise FileNotFoundError("chrome history file 'History' no found")
        super().__init__(name, source_path)
