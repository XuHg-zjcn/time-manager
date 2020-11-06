'''
class and func for my_str, time_str
'''

#set for BigPart
class uset(set):
    #TODO: add method remove, check
    #TODO: use dict
    def add(self, ele):
        if ele in self:
            raise KeyError('element {} already in set:\n{}'.format(ele, self))
        super().add(ele)

def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))

class my_odict(dict):
    def __init__(self):
        super().__init__()
        self.klst = []
    def __setitem__(self, k, v):
        if isinstance(k, int):    #k as index
            assert k<len(self.klst)
            k = self.klst[k]
        if k not in self:
            self.klst.append(k)
        super().__setitem__(k, v)
    def __getitem__(self, k):
        if isinstance(k, int):    #k as index
            k = self.key_list[k]
        return super().__getitem__(k)
    def next_nNone(self, ki, prev_next):
        if prev_next == 1:
            ki += 1
        sli = {1:slice(ki,None,1), -1:slice(0,ki,-1)}[prev_next]
        for k in self.klst[sli]:
            if self[k] is not None:
                return k
        return None
    def get_allow_lr(self, part_obj):
        left = None
        right = None
        for ni,k in enumerate(self.klst):
            v = self[k]
            if v is not None:
                if left is None and v > part_obj:
                    left = ni
                if left is not None and right is None and v < part_obj:
                    right = ni
        return left, right
    def pop():                    #don't delete item
        raise NotImplementedError('my_odict delete is forbidden')
