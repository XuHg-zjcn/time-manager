#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import subprocess as sp
from ffmpy3 import FFmpeg
from commd_line.init_config import init_config

conf = init_config()


class Recoder:
    def __init__(self):
        fn = time.strftime('record_%Y%m%d_%H%M%S.mp4')
        ff = FFmpeg(inputs={'pipe:0': '-f rawvideo -pix_fmt bgr24 -s:v 640x480'},
                    outputs={fn: '-c:v h264 -b:v 500k'})
        self.p = sp.Popen(ff._cmd, stdin=sp.PIPE)

    def write_frame(self, frame):
        self.p.stdin.write(frame.tostring())
