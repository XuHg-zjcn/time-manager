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

class part_lr:
    def __init__(self, part, lr):
        self.part = part
        self.lr = lr
        self.l = lr[0]
        self.r = lr[1]
class parts_insec:
    def __init__(self, part1, part2, insec):
        self.part1 = part1
        self.part2 = part2
        self.insec = insec
class mrange_set(dict): #dict[Part.tuple] = (Part, l, r)
    def __init__(self, from_dict):
        super().__init__(from_dict)
    def intersection(self, i, j):
        sta = max(self[i].l, self[j].l)
        end = min(self[i].r, self[j].r)
        l = end - sta
        if l>0:  return sta, end
        else:  return None
    def get_intersections(self):
        ret = []
        skip = set()
        for i in self:  #i,j are Part.tuple
            skip.add(i)
            for j in self:
                if j in skip:
                    continue
                insec = self.intersection(i,j)
                if insec is not None:
                    ret.append(parts_insec(self[i].part, self[j].part, insec))
        return ret