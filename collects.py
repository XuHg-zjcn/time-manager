#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal

from commd_line.init_config import conf
from analyzers.mtcnn_face import MTCNNFace


def stop(signalnum, handler):
    global mtc
    print('stopping')
    try:  # avoid call in sound play multiprocess raise Error
        mtc.stop()
    except NameError:
        pass


signal.signal(signal.SIGINT, stop)


if __name__ == '__main__':
    db_path = conf['init']['db_path']
    mtc = MTCNNFace(db_path=db_path)
    mtc.start()
