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
cfg_path = 'config.conf'               # don't change, else can't find
conf = configparser.ConfigParser()


def create():
    conf['init'] = {'dir': '.',        # work dir
                    'plot': 'cli',     # plot date-time2d
                    'print_max': 50}   # print output max items
    conf.write(open(cfg_path, 'w'))


def init_config():
    if os.path.exists(cfg_path):
        conf.read(cfg_path)
    else:
        create()
    os.chdir(conf['init']['dir'])
    return conf
