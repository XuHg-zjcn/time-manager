from gi.repository import Notify

from my_libs.time_limit import ExpTimer
from notifys.base_notify import BaseNotify


class GiNotify(BaseNotify):
    def __init__(self):
        Notify.init("time-manager")
        self.et = ExpTimer(2, 5)

    def once(self, title, text):
        if self.et.acquire():
          Notify.Notification.new(title, text).show()
