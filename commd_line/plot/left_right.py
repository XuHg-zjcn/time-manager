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
    """
    IntervalTree's range: range to color
    IntervalTree's data: color name, see _color1
    """

    def __init__(self, ivtree, defalut_color='r', space_color='k', end=96*8):
        """
        Init Syncer.

        ivtree: The IntervalTree object
        defalut_color: use to Intervals without data
        space_color: color for IntervalTree not overlap ranges
        """
        if ivtree.begin() < 0:
            raise ValueError('IntervalTree begin{} < 0'
                             .format(ivtree.begin()))
        if ivtree.end() > end:
            raise ValueError('IntervalTree end{} > fill end{}'
                             .format(ivtree.end(), end))
        self.tree = ivtree
        self._apply_defalut_color(defalut_color)
        self._insert_space(space_color, end)
        self._out_str = ''          # len(out_str) include contral chara
        self._outn = 0              # blocks in out_str

    def _apply_defalut_color(self, defalut_color):
        for iv in self.tree:
            if iv.data is None:
                iv.data = defalut_color

    def _insert_space(self, space_color, end):
        iv0 = Interval(0, self.tree.begin(), space_color)
        for iv1 in sorted(self.tree):
            if iv1.begin != iv0.end:
                self.tree[iv0.end:iv1.begin] = space_color
            iv0 = iv1
        if iv0.end != end:
            self.tree[iv0.end:end] = space_color

    def fill(self):
        """Fill IntervalTree to output string."""
        while True:
            o8 = self._outn*8
            in8 = self.tree[o8:o8+8]
            if len(in8) == 0:
                break
            elif len(in8) == 1:
                in8 = list(in8)[0]
                n = (in8.end - o8)//8
                if n == 0:
                    break
                self._color1(n, in8.data)
            elif len(in8) == 2:
                in8 = sorted(in8)
                assert in8[0].end == in8[1].begin
                spt = in8[0].end % 8
                self._color2(spt, in8[0].data, in8[1].data)
            else:
                break

    def _color2(self, spt, c1, c2):
        """
        Append a block two color to output string.

        spt: spilt point, 0<x<8, chooise unicode
        c1: left side color, see _color1
        c2: right side color
        """
        assert 0 < spt < 8
        assert 0 <= len(c1) <= 1
        assert 0 <= len(c2) <= 1
        stycd = style_code(c1.upper()+c2.lower())
        unicode = left_black[spt]
        self._outn += 1
        self._out_str += stycd+unicode+fend

    def _color1(self, n, c):
        """
        Append blocks same color to output string.

        n: number of blocks
        c: color of blocks, color name char, allow above:
        'r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'
        """
        assert n > 0
        stycd = style_code(c.upper())
        unicode = '█' * n
        self._outn += n
        self._out_str += stycd+unicode

    def get(self):
        """Get output string."""
        return self._out_str + fend


def sync_ivtree(*args, **kwargs):
    """Shortcut to use Syncer."""
    syn = Syncer(*args, **kwargs)
    syn.fill()
    return syn.get()


# test code
if __name__ == '__main__':
    print(sync_ivtree(IvTree2([Iv2(0, 1, 'r'),
                               Iv2(1, 63, 'w'),
                               Iv2(64, 553, 'k'),
                               Iv2(553, 768, 'c')])))
