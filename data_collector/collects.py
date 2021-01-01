#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
from data_collector.camera.mtcnn_face import MTCNNFace


def stop(signalnum, handler):
    global mtc
    mtc.stop()


signal.signal(signal.SIGINT, stop)


if __name__ == '__main__':
    mtc = MTCNNFace()
    mtc.start()
