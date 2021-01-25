#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time

import cv2
from mtcnn import MTCNN

from commd_line.init_config import conf
from .base_checker import Checker
from .face import Face
from my_libs.my_process import ThrRunn


class MTCNNFace(ThrRunn, Checker):
    def __init__(self, inps, callbacks=None, div=int(conf['camera']['div'])):
        # don't use CUDA, start is slow, run speed nearly CPU.
        ThrRunn.__init__(self, inps, callbacks)
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        self.det = MTCNN(steps_threshold=[0.4,0.5,0.5])
        self.div = div
        self.frames = 0

    def once(self, img):
        t_cap = time.time()
        self.frames += 1
        half = cv2.resize(img, dsize=None, fx=1/self.div, fy=1/self.div)
        result = self.det.detect_faces(half)
        faces = []
        for res_d in result:
            face = Face(0, t_cap, self.frames, res_d, img.shape, self.div)
            faces.append(face)
        return faces
