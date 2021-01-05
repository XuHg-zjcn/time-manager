from numbers import Number

from threading import Thread
from threading import Semaphore
from queue import Queue

from multiprocessing import Process
from multiprocessing import Semaphore as pSemaphore
from multiprocessing import Queue as pQueue

from my_libs.timer import SemTimer


class Base:
    def before(self):
        pass

    def once(self, inp):
        return None

    def after(self):
        pass


brk = object()


class Runn(Base):
    objs = []

    def __init__(self, inps=None, callbacks=None):
        Base.__init__(self)
        if callbacks is None:
            callbacks = []
        self.inps = inps
        self.callbacks = callbacks
        self.objs.append(self)

    def run(self):
        self.before()
        while True:
            obj = self.inps()
            if obj is brk:
                break
            ret = self.once(obj)
            if ret is not None:
                for cb in self.callbacks:
                    cb(ret)
        self.after()

    def stop(self):
        pass


class Sem2Queue:
    def __init__(self, sem):
        self.sem = sem

    def put(self, item=None):
        if item is brk:
            self.sem._value = -1
        self.sem.release()

    def get(self, blocking=True, timeout=None):
        if self.sem._value >= 0:
            return self.sem.acquire(blocking, timeout)
        else:
            return brk


class ThrRunn(Runn, Thread):
    def __init__(self, inps, callbacks=None):
        """
        :para inps: can be str 'sem' or 'queue', second of period, callable object.
        'sem': create Sem2Queue object, `self.inp2.put()` run once, `self.inp2(brk)` stop running
        'queue': create a Queue for input `self.inp2 = Queue()`
        float/int: second of period
        callable object: call for get data
        """
        if inps == 'sem':
            self.inp2 = Sem2Queue(Semaphore(0))
        elif inps == 'queue':
            self.inp2 = Queue()
        elif isinstance(inps, Number):
            self.inp2 = Sem2Queue(SemTimer(inps))
        else:
            self.inp2 = None
        if self.inp2:
            inps = self.inp2.get
        Thread.__init__(self)
        Runn.__init__(self, inps, callbacks)

    def before(self):
        if hasattr(self.inp2, 'sem') and isinstance(self.inp2.sem, SemTimer):
            self.inp2.sem.start()

    def stop(self):
        if hasattr(self.inp2, 'sem') and isinstance(self.inp2.sem, SemTimer):
            self.inp2.sem.stop()
        if hasattr(self.inp2, 'put'):
            self.inp2.put(brk)
        self.join()


class ProcRunn(Runn, Process):
    def __init__(self, inps, callbacks=None):
        """
        see class `ThrRunn`, Queue and Semaphore is already instead by multiprocessing object.
        """
        if self.inps == 'sem':
            self.inp2 = Sem2Queue(pSemaphore(0))
        elif self.inps == 'queue':
            self.inp2 = pQueue()
        elif isinstance(self.inps, Number):
            tim = SemTimer(self.inps)
            self.inp2 = Sem2Queue(tim)
            tim.start()
        else:
            self.inp2 = None
        if self.inp2:
            inps = self.inp2.get
        Process.__init__(self)
        Runn.__init__(self, inps, callbacks)
        self.inps = inps

    def stop(self):
        if hasattr(self.inp2, 'sem') and isinstance(self.inp2.sem, SemTimer):
            self.inp2.sem.stop()
        if hasattr(self.inp2, 'put'):
            self.inp2.put(brk)
        self.join()


def stop_all():
    for runn in Runn.objs[::-1]:  # revise stop
        runn.stop()
