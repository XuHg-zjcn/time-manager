import time
from commd_line.init_config import init_config
from .base_checker import Checker
from checks.gen_sound import eye_screen

conf = init_config()


class AreaChecker(Checker):
    def __init__(self):
        self.max_area = int(conf['camera']['face_area_warn'])
        self.n_warn = 0
        super().__init__()

    def check(self, face):
        box = face.res_d['box']
        area = box[2] * box[3]
        if area > self.max_area:
            self.n_warn += 1
            print('face area warning {} at {}, mind your eyes keep away from screen'
                  .format(self.n_warn, time.strftime('%H:%M:%S')))
            return True
        return False


class FaceCheckers(list):
    def __init__(self):
        super().__init__()
        self.append(AreaChecker())
        self.sound = eye_screen()

    def check_all(self, face):
        warn = False
        for c in self:
            warn |= c.check(face)
        if warn:
            self.sound.play_thread()
