#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import cv2
from mtcnn import MTCNN
from ..timer import RepeatingTimer
from .video_recoder import Recoder
from commd_line.init_config import init_config
from .sqlite_face import FaceDB
from .face import Face
from checks.face_check import FaceCheckers

conf = init_config()


class MTCNNFace:
    def __init__(self, period=float(conf['camera']['period']),
                       codec=conf['camera']['codec'],
                       crf=int(conf['camera']['crf']),
                       db_path=None):
        # don't use CUDA, start is slow, run speed nearly CPU.
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        self.cap = cv2.VideoCapture(0)
        self.rec = Recoder(codec, crf)
        self.det = MTCNN(steps_threshold=[0.4,0.5,0.5])
        self.fdb = FaceDB(db_path) if db_path else None
        prepare = self.fdb.auto_create_table if self.fdb else None
        self.tim = RepeatingTimer(period, self.a_frame, prepare=prepare)
        self.checker = FaceCheckers()
        self.frames = 0

    def a_frame(self):
        _, frame = self.cap.read()
        t_cap = time.time()
        self.frames += 1
        half = cv2.resize(frame, dsize=None, fx=1/2, fy=1/2)
        result = self.det.detect_faces(half)
        for res_d in result:
            face = Face(0, t_cap, self.frames, res_d)
            if self.fdb:
                self.fdb.write_face(face)
            face.draw_cv(frame)
            self.checker.check_all(face)
        self.rec.write_frame(frame)
        cv2.imshow("cap", frame)  # move to main thread

    def start(self):
        self.tim.start()

    def stop(self):
        self.tim.stop()
        self.cap.release()
        self.rec.stop()
        cv2.destroyAllWindows()
