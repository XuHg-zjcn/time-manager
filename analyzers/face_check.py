import time
import math
from commd_line.init_config import init_config
from .base_checker import Checker
from notifys.gen_sound import eye_screen

conf = init_config()


class AreaChecker(Checker):
    def __init__(self):
        self.f35mm = float(conf['camera']['f35mm'])
        self.face_cm2 = float(conf['camera']['face_cm2'])
        self.face_dis_cm = float(conf['camera']['face_dis_cm'])
        self.n_warn = 0
        self.sound = eye_screen()
        Checker.__init__(self)

    def check_one(self, face):
        box = face.res_d['box']
        area_pix = box[2] * box[3]
        shape = list(map(lambda x: x//face.div, face.shape))
        a = math.sqrt(shape[0]**2 + shape[1]**2)/43.27*self.f35mm
        b = math.sqrt(self.face_cm2)/math.sqrt(area_pix)
        distance = a*b
        if distance < self.face_dis_cm:
            self.n_warn += 1
            print('warning {:d}th at {:s}, face distance={:4.1f}cm, mind your eyes keep away from screen'
                  .format(self.n_warn, time.strftime('%H:%M:%S'), distance))
            self.sound.play()
            return True
        return False

    def once(self, obj):
        for face in obj:
            self.check_one(face)
