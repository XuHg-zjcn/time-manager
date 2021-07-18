from re import I
from .browser.firefox_history import FirefoxHistory
from .browser.chrome_history import ChromeHistory
from .linux_wtmp import wtmp_db
from .gitlog import GitLog


lst = [FirefoxHistory, ChromeHistory, wtmp_db, GitLog]

def input_choose_coll():
    # TODO: gen print form lst
    inp = input('请输入预设编号，可以同时输入多个，用逗号隔开\n'
                '0: firefox(linux)\n'
                '1: chrome(linux)\n'
                '2: linux wtmp日志\n'
                '3: git 日志')
    return lst[int(inp)]
