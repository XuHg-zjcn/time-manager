import math
from commd_line.init_config import conf
from .base_checker import Checker


class AreaChecker(Checker):
    def __init__(self):
        self.f35mm = float(conf['camera']['f35mm'])
        self.face_cm2 = float(conf['camera']['face_cm2'])
        super().__init__()

    def check_one(self, face):
        box = face.res_d['box']
        area_pix = box[2] * box[3]
        shape = list(map(lambda x: x//face.div, face.shape))
        a = math.sqrt(shape[0]**2 + shape[1]**2)/43.27*self.f35mm
        b = math.sqrt(self.face_cm2)/math.sqrt(area_pix)
        distance = a*b
        return distance

    def once(self, obj):
        if len(obj) > 0:
            return min(map(lambda x: self.check_one(x), obj))
