import cv2
from collectors.collect import Collect
from my_libs.my_process import ThrRunn


class Camera(Collect, ThrRunn):
    def __init__(self, inps, callbacks=None):
        Collect.__init__(self)
        ThrRunn.__init__(self, inps, callbacks)
        self.cap = cv2.VideoCapture(0)
        self.shape = self.cap.read()[1].shape

    def once(self, obj):
        _, frame = self.cap.read()
        return frame

    def after(self):
        self.cap.release()
