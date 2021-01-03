#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess as sp
from ffmpy3 import FFmpeg


class Recoder:
    def __init__(self, codec, crf):
        if not os.path.isdir('./videos'):
            os.mkdir('./videos')
        fn = time.strftime('./videos/record_%Y%m%d_%H%M%S.mp4')
        ff = FFmpeg(inputs={'pipe:0': '-f rawvideo -pix_fmt bgr24 -s:v 640x480'},
                    outputs={fn: '-c:v {} -crf {}'.format(codec, crf)})
        # bufsize >= 1 frame raw image size
        self.p = sp.Popen(ff._cmd, stdin=sp.PIPE, bufsize=1000000)

    def write_frame(self, frame):
        self.p.stdin.write(frame.tostring())

    def stop(self):
        # don't kill subprocess, else video file maybe broken!
        self.p.stdin.write('q'.encode('ascii'))
        try:  # ffmpeg will print info after encode.
            self.p.communicate(timeout=3)
        except sp.TimeoutExpired:
            print('exit ffmpeg failed, kill the process')
            self.p.kill()
