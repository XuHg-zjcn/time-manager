#!/usr/bin/python
# coding:utf-8
# copy from https://blog.csdn.net/qq_38412868/article/details/100711702
import time
from threading import Thread, Semaphore


class RepeatingTimer(Thread):
    def __init__(self, period, target=None, args=(), kwargs=None):
        self.period = period
        self.running = False
        self.thr = None
        self.sem = Semaphore()
        super().__init__(target=target, args=args, kwargs=kwargs)

    def thread(self):
        while self.running:
            self.sem.acquire()
            self._target(*self._args, **self._kwargs)

    def run(self):
        self.running = True
        self.thr = Thread(target=self.thread)
        self.thr.start()
        while self.running:
            self.sem.release()
            time.sleep(self.period)

    def stop(self):
        self.running = False
        self.thr.join(self.period*2)
