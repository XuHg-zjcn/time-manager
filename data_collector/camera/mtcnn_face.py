#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import cv2
from mtcnn import MTCNN
from ..timer import RepeatingTimer
from .video_recoder import Recoder
from commd_line.init_config import init_config

conf = init_config()


def points_X2(src):
    ret = {}
    for k, i in src.items():
        ret[k] = tuple(map(lambda x: 2*x, i))
    return ret

def point_X2(src):
    return tuple(map(lambda x: 2 * x, src))


class MTCNNFace:
    def __init__(self, period=float(conf['camera']['period']),
                       codec=conf['camera']['codec'],
                       crf=int(conf['camera']['crf'])):
        # don't use CUDA, start is slow, run speed nearly CPU.
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        self.cap = cv2.VideoCapture(0)
        self.rec = Recoder(codec, crf)
        self.det = MTCNN(steps_threshold=[0.4,0.5,0.5])
        self.tim = RepeatingTimer(period, self.a_frame)

    def a_frame(self):
        _, frame = self.cap.read()
        half = cv2.resize(frame, dsize=None, fx=1/2, fy=1/2)
        result = self.det.detect_faces(half)
        if len(result) > 0:
            bounding_box = point_X2(result[0]['box'])
            keypoints = points_X2(result[0]['keypoints'])

            cv2.rectangle(frame,
                          (bounding_box[0], bounding_box[1]),
                          (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                          (0, 155, 255), 2)

            cv2.circle(frame, (keypoints['left_eye']), 2, (0, 155, 255), 2)
            cv2.circle(frame, (keypoints['right_eye']), 2, (0, 155, 255), 2)
            cv2.circle(frame, (keypoints['nose']), 2, (0, 155, 255), 2)
            cv2.circle(frame, (keypoints['mouth_left']), 2, (0, 155, 255), 2)
            cv2.circle(frame, (keypoints['mouth_right']), 2, (0, 155, 255), 2)

        self.rec.write_frame(frame)
        cv2.imshow("cap", frame)  # move to main thread

    def start(self):
        self.tim.start()

    def stop(self):
        self.tim.stop()
        self.cap.release()
        self.rec.stop()
        cv2.destroyAllWindows()
