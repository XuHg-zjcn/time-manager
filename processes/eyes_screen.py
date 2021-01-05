from collectors.camera import Camera
from collectors.timer import SemTimer
from analyzers.mtcnn_face import MTCNNFace
from analyzers.face_check import AreaChecker
from recorders.video_recoder import VideoRecoder
from recorders.sqlite_face import FaceDB
from queue import Queue

tim = SemTimer(0.5)
que_rec = Queue()
que_mtc = Queue()
que_fdb = Queue()
ac = AreaChecker()
cam = Camera(tim.acquire, (que_rec.put, que_mtc.put))
rec = VideoRecoder(que_rec.get)
mtc = MTCNNFace(que_mtc.get, (ac.once, que_fdb.put))
fdb = FaceDB(que_fdb.get)

if __name__ == '__main__':
    cam.start()
    rec.start()
    mtc.start()
    fdb.start()
    tim.start()
