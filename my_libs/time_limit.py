import math
import time


class TimeLimit:
    def __init__(self, x_sec, x_cap, x_init=None):
        self.x_sec = x_sec
        self.x_cap = x_cap
        self.x = x_init if x_init is not None else x_cap
        self.last = time.time()

    def current_x(self, t=None):
        return 1

    def wait_t(self, x1):
        return 0

    def acquire(self, block=True):
        t1 = time.time()
        x1 = self.current_x(t1)
        if x1 >= 1:
            self.x = x1 - 1
            self.last = t1
            return True
        else:
            if block:
                dt = self.wait_t(x1)
                time.sleep(dt)
                assert self.acquire(block=False)
                return True
            return False


class LinTimer(TimeLimit):
    def current_x(self, t=None):
        if t is None:
            t = time.time()
        x1 = self.x + (t-self.last)/self.x_sec
        if x1 > self.x_cap:
            x1 = self.x_cap
        return x1

    def wait_t(self, x1):
        return (1-x1)*self.x_sec


class ExpTimer(TimeLimit):
    def __init__(self, x_sec, x_cap):
        """
        :para x_sec: sec per
        :para x_cap: cap

        y = Ce^(t/a) + b
        y1 = e^(dt/a) * (y0-b) + b
        """
        super().__init__(x_sec, x_cap)
        self.a = math.log(x_cap/(x_cap+1))/x_sec

    def current_x(self, t=None):
        if t is None:
            t = time.time()
        return math.exp(self.a*(t-self.last)) * (self.x-self.x_cap) + self.x_cap

    def wait_t(self, x1):
        return math.log((self.x_cap - 1) / (self.x_cap - x1)) / self.a
