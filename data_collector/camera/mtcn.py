#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import cv2
from mtcnn import MTCNN
from video_recoder import Recoder
from commd_line.init_config import init_config

conf = init_config()


def points_X2(src):
    ret = {}
    for k, i in src.items():
        ret[k] = tuple(map(lambda x: 2*x, i))
    return ret

def point_X2(src):
    return tuple(map(lambda x: 2*x, src))

if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    cap = cv2.VideoCapture(0)
    detector = MTCNN(steps_threshold=[0.4,0.5,0.5])
    rec = Recoder()
    while 1:
        ret, frame = cap.read()
        t0 = time.time()
        half = cv2.resize(frame, dsize=None, fx=1/2, fy=1/2)
        result = detector.detect_faces(half)
        t1 = time.time()
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

        rec.write_frame(frame)
        cv2.imshow("cap", frame)
        if cv2.waitKey(100) & 0xff == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
