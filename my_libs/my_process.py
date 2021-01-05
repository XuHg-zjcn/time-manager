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
    """
    if use second of period, please call `super().before()` in rewrite before method
    """
    objs = []

    def __init__(self, inps=None, callbacks=None, inp2=None):
        Base.__init__(self)
        if callbacks is None:
            callbacks = []
        self.inps = inps
        self.callbacks = callbacks
        self.inp2 = inp2
        self.will_stop = 0  # 0: OK, 1: wait to empty, 2: stop now
        self.objs.append(self)

    def before(self):
        if isinstance(self.inp2, SemTimer):
            self.inp2.start()

    def run(self):
        self.before()
        while (not self.will_stop)\
                or (hasattr(self.inp2, '_value') and self.inp2._value != 0)\
                or (hasattr(self.inp2, 'qsize') and self.inp2.qsize() != 0):
            obj = self.inps()
            if self.will_stop == 2 or obj is brk:
                break
            ret = self.once(obj)
            if ret is not None:
                for cb in self.callbacks:
                    cb(ret)
        self.after()

    def join(self):
        pass

    def stop(self):
        self.will_stop = 1
        if isinstance(self.inp2, SemTimer):
            self.inp2.stop()
        if hasattr(self.inp2, 'release') and self.inp2._value == 0:
            self.will_stop = 2
            self.inp2.release()
        if hasattr(self.inp2, 'put'):
            self.inp2.put(brk)
        self.join()


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
            inp2 = Semaphore(0)
            inps = inp2.acquire
        elif inps == 'queue':
            inp2 = Queue()
            inps = inp2.get
        elif isinstance(inps, Number):
            inp2 = SemTimer(inps)
            inps = inp2.acquire
        else:
            inp2 = None
        Thread.__init__(self)
        Runn.__init__(self, inps, callbacks, inp2)


class ProcRunn(Runn, Process):
    def __init__(self, inps, callbacks=None):
        """
        see class `ThrRunn`, Queue and Semaphore is already instead by multiprocessing object.
        """
        if self.inps == 'sem':
            inp2 = pSemaphore(0)
            inps = inp2.acquire
        elif self.inps == 'queue':
            inp2 = pQueue()
            inps = inp2.get
        elif isinstance(self.inps, Number):
            inp2 = SemTimer(self.inps)
            inps = inp2.acquire
        else:
            inp2 = None
        Process.__init__(self)
        Runn.__init__(self, inps, callbacks, inp2)


def stop_all():
    for runn in Runn.objs[::-1]:  # revise stop
        runn.stop()
