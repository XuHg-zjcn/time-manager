#!/bin/python
import os
import configparser
import sqlite3

finds = map(lambda x: '../'*x + 'time-manager', range(4))
found = False
for path in finds:
    if os.path.exists(path):
        found = True
        os.chdir(path)
        break
if not found:
    raise FileNotFoundError("'time-manager' dir not found, "
                            "please don't change project dir name.")
if not os.path.exists('user_data'):
    os.mkdir('user_data')  # create 'user_data' foloder
os.chdir('user_data')

cfg_path = 'config.ini'               # don't change, else can't find
conf = configparser.ConfigParser()


# TODO: char_hour, force_bar
def create():
    conf['init'] = {'dir': '.',
                    'db_path': 'tasks.db',
                    'table_name': 'real_record'}  # work dir
    conf['show'] = {'type': 'pyqtgraph',  # plot date-time2d
                    'char_hour': 4,     # char per hour
                    'print_minN': 5,    # print N found min items
                    'print_max': 50,    # print output max item, >= 2*print_side
                    'print_side': 20,   # print over max item, middle use '...'
                    'force_bar': 20}    # force print each item
    conf['camera'] = {'period': 0.5,
                      'face_detector': 'MTCNN',  # unused
                      'codec': 'hevc',
                      'crf': 30,        # don't use constant bitrate!, because quality not balance.
                      'div': 2,         # image div for face detection, must
                      'f35mm': 34.6,    # 35mm equivalent focal length
                      'face_cm2': 230,  # face area for warning eyes near to screen
                      'face_dis_cm_L': 40,  # trigger to send warning
                      'face_dis_cm_H': 45}  # trigger to stop warning
    conf.write(open(cfg_path, 'w'))


if os.path.exists(cfg_path):
    conf.read(cfg_path)
else:
    create()
os.chdir(conf['init']['dir'])
conn = sqlite3.connect(conf['init']['db_path'])
