#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess as sp

from ffmpy3 import FFmpeg

from .record import Record
from my_libs.my_process import ThrRunn
from commd_line.init_config import conf


class VideoRecoder(ThrRunn, Record):
    def __init__(self, inps,
                 codec=conf['camera']['codec'],
                 crf=float(conf['camera']['crf'])):
        ThrRunn.__init__(self, inps)
        Record.__init__(self)
        self.codec = codec
        self.crf = crf
        self.size = None
        self.p = None

    def before(self):
        if not all([self.codec, self.crf, self.size]):
            return
        if self.p:
            return
        if not os.path.isdir('./videos'):
            os.mkdir('./videos')
        fn = time.strftime('./videos/record_%Y%m%d_%H%M%S.mp4')
        ff = FFmpeg(inputs={'pipe:0': '-f rawvideo -pix_fmt bgr24 -s:v {}x{}'.format(*self.size)},
                    outputs={fn: '-c:v {} -crf {}'.format(self.codec, self.crf)})
        bufsize = int(self.size[0] * self.size[1] * 3 * 1.05) + 1000
        self.p = sp.Popen(ff._cmd, stdin=sp.PIPE, bufsize=bufsize)

    def once(self, frame):
        if not self.p:
            self.size = (frame.shape[1], frame.shape[0])
            self.before()
        self.p.stdin.write(frame.tostring())

    def after(self):
        # don't kill subprocess, else video file maybe broken!
        self.p.stdin.write('q'.encode('ascii'))
        try:  # ffmpeg will print info after encode.
            self.p.communicate(timeout=3)
        except sp.TimeoutExpired:
            print('exit ffmpeg failed, kill the process')
            self.p.kill()
