from intervaltree import Interval, IntervalTree
from .colors import style_code
import sys
sys.path.append('../../')
from my_libs.ivtree2 import IvTree2
from my_libs.ivtree2 import Iv2
resv = '\033[7m'
fend = '\033[0m'
left_black = ' ▏▎▍▌▋▊▉█'


class Syncer:
    def __init__(self, ivtree, defalut_color='r', space_color='k', end=96*8):
        if ivtree.begin() < 0:
            raise ValueError('IntervalTree begin{} < 0'
                             .format(ivtree.begin()))
        if ivtree.end() > end:
            raise ValueError('IntervalTree end{} > fill end{}'
                             .format(ivtree.end(), end))
        self.tree = ivtree
        self.apply_defalut_color(defalut_color)
        self.insert_space(space_color, end)
        self.out_str = ''          # len(out_str) include contral chara
        self.outn = 0              # blocks in out_str

    def apply_defalut_color(self, defalut_color):
        for iv in self.tree:
            if iv.data is None:
                iv.data = defalut_color

    def insert_space(self, space_color, end):
        iv0 = Interval(0, self.tree.begin(), space_color)
        for iv1 in sorted(self.tree):
            if iv1.begin != iv0.end:
                self.tree[iv0.end:iv1.begin] = space_color
            iv0 = iv1
        if iv0.end != end:
            self.tree[iv0.end:end] = space_color

    def fill(self):
        while True:
            o8 = self.outn*8
            in8 = self.tree[o8:o8+8]
            if len(in8) == 0:
                break
            elif len(in8) == 1:
                in8 = list(in8)[0]
                n = (in8.end - o8)//8
                if n == 0:
                    break
                self.color1(n, in8.data)
            elif len(in8) == 2:
                in8 = sorted(in8)
                assert in8[0].end == in8[1].begin
                spt = in8[0].end%8
                self.color2(spt, in8[0].data, in8[1].data)
            else:
                break

    def color2(self, spt, c1, c2):
        assert 0 < spt <= 8
        assert 0 <= len(c1) <= 1
        assert 0 <= len(c2) <= 1
        stycd = style_code(c1.upper()+c2.lower())
        unicode = left_black[spt]
        self.outn += 1
        self.out_str += stycd+unicode+fend

    def color1(self, n, c):
        assert n > 0
        stycd = style_code(c.upper())
        unicode = '█' * n
        self.outn += n
        self.out_str += stycd+unicode

    def end(self):
        return self.out_str + fend


def sync_ivtree(*args, **kwargs):
    syn = Syncer(*args, **kwargs)
    syn.fill()
    return syn.end()

if __name__ == '__main__':
    #print(sync_ivtree([10, 12, 24, 25], ['r', 'w', 'k', 'c']))
    print(sync_ivtree(IvTree2([Iv2(0, 1, 'r'),
                               Iv2(1, 63, 'w'),
                               Iv2(64, 553, 'k'),
                               Iv2(553, 768, 'c')]),
                      'r'))
