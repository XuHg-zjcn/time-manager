import os
import time

class net_mgr:
    net_off = "nmcli dev disconnect enp2s0"
    net_on  = "nmcli dev connect enp2s0"
    
    def __init__(self):
        self.last_time = time.time()
    
    def get_time(self):
        t1 = time.time()
        dt = t1 - self.last_time
        self.last_time = t1
        return dt
    
    def on(self):
        os.system(net_mgr.net_on)
        return self.get_time()
        
    def off(self):
        os.system(net_mgr.net_off)
        return self.get_time()
