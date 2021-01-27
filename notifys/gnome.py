from gi.repository import Notify

from my_libs.time_limit import TimeLimit
from notifys.base_notify import BaseNotify


class GiNotify(BaseNotify):
    def __init__(self):
        Notify.init("time-manager")
        self.tl = TimeLimit(2, 5)

    def once(self, title, text):
        if self.tl.acquire():
          Notify.Notification.new(title, text).show()
