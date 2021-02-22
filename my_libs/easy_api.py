import math
import numpy as np
from playsound import playsound
import sounddevice as sd

from commd_line.init_config import conf
from notifys.gnome import GiNotify
from notifys.gen_sound import SoundGene

gi = GiNotify()
pi = math.pi


def message(title, text):
    gi.once(title, text)


def sound(x):
    if isinstance(x, str):
        playsound(f'./sounds/{x}.wav')
    elif isinstance(x, SoundGene):
        x.once(True)
    elif isinstance(x, np.ndarray) and x.ndim == 1:
        if x.shape[0] < 44100*0.05:
            s = 'short'
        elif x.shape[0] > 44100*60:
            s = 'long'
        else:
            s = ''
        if s:
            print(f'warning: sound too {s}, {x.shape[0]/44100}s, '
                  'default samplerate=44100Hz')
        sd.play(x, 44100)
    else:
        raise TypeError('unsupported type', type(x))
