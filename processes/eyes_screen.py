from collectors.camera import Camera
from analyzers.value_check import ValueChecker
from analyzers.mtcnn_face import MTCNNFace
from analyzers.face_check import AreaChecker
from recorders.video_recoder import VideoRecoder
from recorders.sqlite_face import FaceDB
from notifys.gen_sound import eye_screen
from notifys.gnome import GiNotify
import signal


def sigint(signalnum, handler):
    print('stopping')
    cam.stop()
    rec.stop()
    mtc.stop()
    fdb.stop()
    sound.stop()

signal.signal(signal.SIGINT, sigint)


gn = GiNotify()
sound = eye_screen('sem')
vc = ValueChecker(45, 50, False)
ac = AreaChecker()


def area2(faces):
    cm = ac.once(faces)
    if cm is None:
        return
    state, diff = vc.once(cm)
    if not state:
        sound.inp2.release()
    if diff == -1:
        gn.once('eye_screen', '{:.1f}cm, mind your eyes keep away from screen'.format(cm))


rec = VideoRecoder('queue')
fdb = FaceDB('queue')
mtc = MTCNNFace('queue', (fdb.inp2.put, area2))
cam = Camera(0.5, (rec.inp2.put, mtc.inp2.put))


def run():
    sound.start()
    cam.start()
    rec.start()
    mtc.start()
    fdb.start()
