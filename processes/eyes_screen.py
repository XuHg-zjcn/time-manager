from collectors.camera import Camera
from collectors.timer import SemTimer
from analyzers.mtcnn_face import MTCNNFace
from analyzers.face_check import AreaChecker
from recorders.video_recoder import VideoRecoder
from collectors.timer import SemTimer
from queue import Queue

tim = SemTimer(0.5)
que_rec = Queue()
que_mtc = Queue()
ac = AreaChecker()
cam = Camera(tim.acquire, (que_rec.put, que_mtc.put))
rec = VideoRecoder(que_rec.get)
mtc = MTCNNFace(que_mtc.get, (ac.once,))

if __name__ == '__main__':
    cam.start()
    rec.start()
    mtc.start()
    tim.start()
