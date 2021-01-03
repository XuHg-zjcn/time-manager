#!/usr/bin/python
# coding:utf-8
# some code copy from https://blog.csdn.net/qq_38412868/article/details/100711702
import time
from threading import Thread, Semaphore


class RepeatingTimer(Thread):
    def __init__(self, period, target=None, args=(), kwargs=None, prepare=None, finish=None):
        """
        don't support args and kwargs for prepare, please use lambda or functools.partial.
        """
        self.period = period
        self.running = False
        self.thr = Thread(target=self.thread)
        self.sem = Semaphore()
        self._prepare = prepare
        self._finish = finish
        super().__init__(target=target, args=args, kwargs=kwargs)

    def thread(self):
        if self._prepare:
            self._prepare()
        while True:
            self.sem.acquire(timeout=self.period)
            if not self.running:
                break
            self._target(*self._args, **self._kwargs)
        if self._finish:
            self._finish()

    def run(self):
        self.running = True
        self.thr.start()
        while self.running:
            self.sem.release()
            time.sleep(self.period)

    def stop(self):
        self.running = False
        self.sem.release()
        self.thr.join(self.period*2)
