from playsound import playsound

from commd_line.init_config import conf
from notifys.gnome import GiNotify

gi = GiNotify()


def message(title, text):
    gi.once(title, text)


def sound(name):
    playsound(f'./sounds/{name}.wav')
