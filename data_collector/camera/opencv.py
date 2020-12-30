#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    path = os.path.join(cv2.__path__[0], 'data/haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(path)
    while 1:
        ret, frame = cap.read()
        frame = cv2.resize(frame, dsize=None, fx=1/2, fy=1/2)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # 绘制人脸矩形框
        for (x, y, w, h) in faces:
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow("cap", frame)
        if cv2.waitKey(100) & 0xff == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
