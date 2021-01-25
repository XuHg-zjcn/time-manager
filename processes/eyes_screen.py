from collectors.camera import Camera
from analyzers.mtcnn_face import MTCNNFace
from analyzers.face_check import AreaChecker
from recorders.video_recoder import VideoRecoder
from recorders.sqlite_face import FaceDB
import signal


def sigint(signalnum, handler):
    print('stopping')
    cam.stop()
    rec.stop()
    mtc.stop()
    fdb.stop()
    ac.sound.stop()

signal.signal(signal.SIGINT, sigint)


ac = AreaChecker()
rec = VideoRecoder('queue')
fdb = FaceDB('queue')
mtc = MTCNNFace('queue', (fdb.inp2.put, ac.once))
cam = Camera(0.5, (rec.inp2.put, mtc.inp2.put))


def run():
    cam.start()
    rec.start()
    mtc.start()
    fdb.start()
