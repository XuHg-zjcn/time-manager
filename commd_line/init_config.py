#!/bin/python
import os
import configparser

finds = map(lambda x: '../'*x + 'user_data', range(4))
found = False
for path in finds:
    if os.path.exists(path):
        found = True
        os.chdir(path)
        break
if not found:
    raise FileNotFoundError("user_data not found.")
cfg_path = 'config.ini'               # don't change, else can't find
conf = configparser.ConfigParser()


# TODO: char_hour, force_bar
def create():
    conf['init'] = {'dir': '.',
                    'db_path':'browser.db',
                    'table_name':'firefox'}  # work dir
    conf['show'] = {'type': 'pyqtgraph',  # plot date-time2d
                    'char_hour': 4,     # char per hour
                    'print_minN': 5,    # print N found min items
                    'print_max': 50,    # print output max item
                    'print_side': 20,   # print over max item, middle use '...'
                    'force_bar': 20}    # force print each item
    conf.write(open(cfg_path, 'w'))


def init_config():
    if os.path.exists(cfg_path):
        conf.read(cfg_path)
    else:
        create()
    os.chdir(conf['init']['dir'])
    return conf
