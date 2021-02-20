import os
from datetime import datetime

import wave
import numpy as np
from playsound import playsound

from my_libs.my_process import ThrRunn
from commd_line.init_config import conf

pi = np.pi
pi2 = pi*2


class WaveWrite(wave.Wave_write):
    def __init__(self, path, sps=44100):
        f = open(path, 'wb')
        super().__init__(f)
        self.setnchannels(1)
        self.setsampwidth(2)
        self.setframerate(sps)

    def t_arange(self, during):
        return np.arange(0, during, 1/self._framerate)

    def writeframes(self, data):
        """
        numpy data in range -1<=x<1, else clip.
        """
        if isinstance(data, np.ndarray):
            data = np.clip(data*32767, -32768, 32767)
            data = data.astype(np.int16).tobytes()
        super().writeframes(data)

    def write_fx(self, during, func):
        data = func(self.t_arange(during))
        self.writeframes(data)


class SoundGene(ThrRunn):
    name = None
    gen = None

    def __init__(self, inps=None, name=None, gen=None):
        super().__init__(inps)
        name = name or self.name or datetime.now().strftime('%Y%m%d_%H%M%S')
        name += '.wav'
        sound_dir = './sounds'
        if not os.path.isdir(sound_dir):
            os.mkdir(sound_dir)
        self.path = os.path.join(sound_dir, name)
        if not os.path.exists(self.path):
            ww = WaveWrite(self.path)
            gen = gen or self.gen
            if gen is None:
                raise ValueError('invalid gen')
            gen(ww)
            ww.close()

    def once(self, obj):
        playsound(self.path)


class eye_screen(SoundGene):
    name = 'eye_screen'

    @staticmethod
    def gen(ww):
        ww.write_fx(0.5, lambda t: 0.5*np.sin(t*5*pi2)*np.sin(t*2000*pi2))
