from threading import Thread
from multiprocessing import Process
from multiprocessing import Value


class Base:
    def before(self):
        pass

    def once(self, inp):
        return None

    def after(self):
        pass


class Runn(Base):
    def __init__(self, inps=None, callbacks=None):
        Base.__init__(self)
        if callbacks is None:
            callbacks = []
        self.inps = inps
        self.callbacks = callbacks

    def is_break(self):
        return False

    def run(self):
        self.before()
        while True:
            obj = self.inps()
            if self.is_break():
                break
            ret = self.once(obj)
            if ret is not None:
                for cb in self.callbacks:
                    cb(ret)
        self.after()

    def stop(self):
        pass


class ThrRunn(Runn, Thread):
    def __init__(self, inps=None, callbacks=None):
        Thread.__init__(self)
        Runn.__init__(self, inps, callbacks)
        self.running = True

    def is_break(self):
        return not self.running

    def stop(self):
        self.running = False
        self.join()


class ProcRunn(Runn, Process):
    def __init__(self, inps=None, callbacks=None):
        Process.__init__(self)
        Runn.__init__(self, inps, callbacks)
        self.running = Value('i', 1)

    def is_break(self):
        return not self.running.value

    def stop(self):
        self.running.value = 0
        self.join()
