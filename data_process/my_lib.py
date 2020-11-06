'''
class and func for my_str, time_str
'''
from collections import Iterable
from my_str import Part
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
    def get_allow_lr(self, part_obj):
        '''
        prev left ... right next
                part_obj
        
        prev and next are not None
        prev.end <= part_obj.start   and   part_obj.end <= next.start
        left = prev+1
        right = next-1
        
        part_obj can add to left<=x<=right
        '''
        left = None
        right = None
        for ni,k in enumerate(self.klst):
            v = self[k]
            if v is not None:
                if left is None and v < part_obj:
                    left = ni + 1  #prev = v
                if left is not None and right is None and v > part_obj:
                    right = ni - 1 #next = v
                if not any([left,right]): #left and right are not None
                    break
        if left is not None and right is None:
            right = len(self.klst) - 1
        if all([left,right]) and left > right:
            return None
        if not any([left,right]):
            return None
        return left, right
    def next_None(self, ki, prev_next):
        l = len(self.klst)
        ki = {1:0, -1:l-1}[prev_next] if ki is None else ki
        sli = {1:(ki,l,1), -1:(ki,-1,-1)}[prev_next]
        for i in range(*sli):
            if self[self.klst[i]] is None:
                return i
        return sli[1]-prev_next
    def pop():                    #don't delete item
        raise NotImplementedError('my_odict delete is forbidden')

class mrange_set(set):
    def __init__(self):
        super().__init__()
    def add(self, span):
        if isinstance(span, Iterable):
            pass
        elif isinstance(span, Part):
            span = Part.span
        else:
            raise ValueError('mrange_set add type invaild!')
        super().add(tuple(span))
    def intersection(i, j):
        sta = max(i.sta, j.end)
        end = min(i.sta, j.end)
        l = end - sta
        if l>0:  return sta, end
        else:  return None
    def intersections(self):
        ret = []
        cont = []
        for i in self:
            cont.append(i)
            for j in self:
                if j in cont:
                    continue
                insec = self.intersection(i,j)
                if insec is not None:
                    ret.append(insec)
        return ret

def as_mr_set(fills_dict):#dict[uup.get_tuple()] = (upp,l,r)
    mr_set = mrange_set()
    for lr in fills_dict.values():
        mr_set.add(lr[1:])
    return mr_set
