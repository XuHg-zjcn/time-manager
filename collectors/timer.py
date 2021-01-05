#!/usr/bin/python
# coding:utf-8
# some code copy from https://blog.csdn.net/qq_38412868/article/details/100711702
import time
from threading import Thread, Semaphore


class SemTimer(Thread, Semaphore):
    def __init__(self, period, delay=0):
        """
        don't support args and kwargs for prepare, please use lambda or functools.partial.
        """
        self.period = period
        self.delay = delay
        self.running = False
        Thread.__init__(self)
        Semaphore.__init__(self, 0)

    def run(self):
        self.running = True
        if self.delay:
            time.sleep(self.delay)
        while True:
            self.release()
            if not self.running:
                break
            time.sleep(self.period)

    def stop(self):
        self.running = False
        self.release()
        self.join(self.period*2)
