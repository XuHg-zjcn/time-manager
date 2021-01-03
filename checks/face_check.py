import time
import math
from commd_line.init_config import init_config
from .base_checker import Checker
from checks.gen_sound import eye_screen

conf = init_config()


class AreaChecker(Checker):
    def __init__(self):
        self.f35mm = float(conf['camera']['f35mm'])
        self.face_cm2 = float(conf['camera']['face_cm2'])
        self.face_dis_cm = float(conf['camera']['face_dis_cm'])
        self.n_warn = 0
        super().__init__()

    def check(self, face, shape):
        box = face.res_d['box']
        area_pix = box[2] * box[3]
        a = math.sqrt(shape[0]**2 + shape[1]**2)/43.27*self.f35mm
        b = math.sqrt(self.face_cm2)/math.sqrt(area_pix)
        distance = a*b
        if distance < self.face_dis_cm:
            self.n_warn += 1
            print('warning {:d}th at {:s}, face distance={:4.1f}cm, mind your eyes keep away from screen'
                  .format(self.n_warn, time.strftime('%H:%M:%S'), distance))
            return True
        return False


class FaceCheckers(list):
    def __init__(self):
        super().__init__()
        self.append(AreaChecker())
        self.sound = eye_screen()

    def check_all(self, face, shape):
        warn = False
        for c in self:
            warn |= c.check(face, shape)
        if warn:
            self.sound.play()
