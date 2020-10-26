import math
class event:
    def __init__(self, time, new_stat:bool, old_stat=None):
        self.time = time
        self.new_stat = new_stat
        if old_stat is None:
            self.old_stat = not new_stat
        elif isinstance(old_stat, bool):
            self.old_stat = old_stat
        else:
            raise ValueError('old_stat must bool or None')

class time_algh:              #type 0
    def __init__(self, idx, minV, maxV):
        self.idx = idx
        self.minV = minV
        self.maxV = maxV
    
    def inRange(self, event):
        if event.time < self.minV:    #low than alloc
            ret = -1
        elif event.time > self.maxV:  #high than alloc
            ret = 1
        else:                         #in alloc range
            ret = 0
        return ret

class min_max(time_algh):
    def update(self, event):
        self.V = event.time
        return self.V, (float('-inf'), float('inf')), self.inRange(event)
        
class mean_integ(time_algh):  #type 1
    def __init__(self, idx, mean, minV, maxV, V0):
        self.mean = mean
        self.V = V0
        super().__init__(idx, minV, maxV)
        self.xdict = {False:-self.mean, True:1}
    
    def update(self, event):
        self.V += event.time*self.xdict[event.old_stat]
        func = lambda x:(x - self.V)/self.xdict[event.new_stat]
        t1 = func(self.minV)
        t2 = func(self.maxV)
        tmin = min(t1, t2)
        tmax = max(t1, t2)
        return self.V, (tmin, tmax), self.inRange(event)

class t_conv(time_algh):      #type 2
    def __init__(self, idx, sec63, minV, maxV, V0):
        self.sec63 = sec63
        self.V = V0
        super().__init__(idx, minV, maxV)
        
    def update(self, event):
        #x(t) = [x(0)-x(+oo)]*e^(-at) + x(+oo)
        #a = time constat, 63% change time
        x0 = self.V
        xoo = int(event.old_stat)
        self.V = (x0-xoo)*math.exp(-event.time/self.sec63) + xoo
        #new stat max time
        xoo = int(event.new_stat)
        def func(x):
            if x0-xoo < 1e-6:        #current is stable
                return float('inf')
            elif (x-xoo/x0-xoo) > 0:
                return -self.sec63*math.log((x-xoo)/(x0-xoo))
            else:
                return float('-inf')
        t1 = func(self.minV)
        t2 = func(self.maxV)
        tmin = min(t1, t2)
        tmax = max(t1, t2)
        return self.V, (tmin, tmax), self.inRange(event)

