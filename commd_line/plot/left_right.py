from intervaltree import Interval, IntervalTree
from .colors import style_code
from .base import gray
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

    def __init__(self, ivtree, defalut_color='b', space_color='k', end=96*8):
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
        self._end = end
        self._insert_space(space_color)
        self._out_str = ''          # len(out_str) include contral chara
        self._outn = 0              # blocks in out_str

    def _insert_space(self, space_color):
        iv0 = Interval(0, 0, space_color)
        for iv1 in sorted(self.tree):
            if iv1.begin != iv0.end:
                self.tree[iv0.end:iv1.begin] = space_color
            iv0 = iv1
        if iv0.end != self._end:
            self.tree[iv0.end:self._end] = space_color

    def fill(self, toomany_color='r'):
        """Fill IntervalTree to output string."""
        while True:
            o8 = self._outn*8
            in8 = sorted(self.tree[o8:o8+8])
            if len(in8) == 0:
                break
            elif len(in8) == 1:
                in8 = in8[0]
                n = (in8.end - o8)//8
                if n == 0:
                    break
                self._color1(n, in8.data)
            elif len(in8) == 2:
                # assert in8[0].end == in8[1].begin  after insert_space
                spt = in8[0].end % 8
                self._color2(spt, in8[0].data, in8[1].data)
            elif len(in8) == 3:
                left = in8[0].end
                right = in8[1].end
                if left < 8-right and left <= 2:
                    left_border = o8
                    # modify 0 end and 1 begin to right_border
                    self._change_border(in8[0], in8[1], left_border)
                elif left > 8-right and 8-right <= 2:
                    right_border = o8 + 8
                    # modify 1 end and 2 begin to right_border
                    self._change_border(in8[1], in8[2], right_border)
                elif left <= 1 and 8-right <= 1:
                    pass
                else:
                    self.gray_show(in8, o8)
            elif len(in8) == 4:
                self.gray_show(in8, o8)
            else:
                if len(in8) < 10:
                    char = str(len(in8))
                else:
                    char = '+'
                M = self._most_iv(in8, o8)
                # M.data to backgroud, toomany_color to foreground
                stycd = style_code(toomany_color, M.data)
                self._outn += 1
                self._out_str += stycd + char

    def _change_border(self, iv0, iv1, new_border):
        self.tree.remove(iv0)
        self.tree.remove(iv1)
        self.tree.addi(iv0.begin, new_border, iv0.data)
        self.tree.addi(new_border, iv1.end, iv1.data)

    def _most_iv(self, in8, o8):
        insec = IvTree2(in8) & Iv2(o8, o8+8)
        return max(insec, key=lambda x: x.length())

    def _gray_show(self, in8, o8):
        M = self._most_iv(in8, o8)
        n_gray = (M.length() + 1)//2
        gray_char = gray[n_gray]
        self._color1(1, M.data, gray_char)

    def _color2(self, spt, c1, c2):
        """
        Append a block two color to output string.

        spt: spilt point, 0<x<8, chooise unicode
        c1: left side color, see _color1
        c2: right side color
        """
        assert 0 < spt < 8
        stycd = style_code(c1, c2)
        char = left_black[spt]
        self._outn += 1
        self._out_str += stycd + char + fend

    def _color1(self, n, c, char='█'):
        """
        Append blocks same color to output string.

        n: number of blocks
        c: color of blocks, color name char, allow above:
        'r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'
        """
        assert n > 0
        stycd = style_code(c, None)
        self._outn += n
        self._out_str += stycd + char*n

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
