from .browser.firefox_history import FirefoxHistory
from .browser.chrome_history import ChromeHistory


lst = [FirefoxHistory, ChromeHistory]

def input_choose_coll():
    inp = input('请输入预设编号，可以同时输入多个，用逗号隔开\n'
                '0: firefox(linux)\n'
                '1: chrome(linux)\n')  # TODO: gen print form lst
    return lst[int(inp)]()
