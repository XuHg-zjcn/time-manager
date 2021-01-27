from analyzers.base_checker import Checker


class ValueChecker(Checker):
    def __init__(self, vL, vH, init_state=False):
        self.vH = vH
        self.vL = vL
        self.state = init_state

    def once(self, inp):
        old = self.state
        if inp > self.vH:
            self.state = True
        if inp < self.vL:
            self.state = False
        diff = self.state - old
        return self.state, diff
