import os
import wave
from multiprocessing import Process, Semaphore
import numpy as np
from playsound import playsound
from commd_line.init_config import init_config

conf = init_config()

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


class SoundGene:
    def __init__(self, name=None):
        if name is None:
            name = self.__class__.__name__ + '.wav'
        sound_dir = './sounds'
        if not os.path.isdir(sound_dir):
            os.mkdir(sound_dir)
        self.path = os.path.join(sound_dir, name)
        if not os.path.exists(self.path):
            ww = WaveWrite(self.path)
            self.process(ww)
            ww.close()
        self.sem = Semaphore(0)
        self.proc = Process(target=self.thread, args=(self.sem,))
        self.proc.start()

    def process(self, ww):
        pass

    def thread(self, sem):
        while True:
            sem.acquire()
            playsound(self.path)

    def play(self):
        self.sem.release()

    def kill_process(self):
        self.proc.kill()

class eye_screen(SoundGene):
    def process(self, ww):
        ww.write_fx(0.5, lambda t: 0.5*np.sin(t*5*pi2)*np.sin(t*2000*pi2))
