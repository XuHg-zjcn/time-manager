
from plot.colors import style_code
resv = '\033[7m'
fend = '\033[0m'
left_black = ' ▏▎▍▌▋▊▉█'


class group:
    def __init__(self, color, end):
        self.color = color
        self.end = end


class syncer:
    def __init__(self):
        self.out_str = ''          # len(out_str) include contral chara
        self.outn = 0              # blocks in out_str
        self._tmp = []             # temp group

    def add(self, end, color):
        self._tmp.append(group(color, end))
        self.fill()

    def fill(self):
        while len(self._tmp) != 0 and self._tmp[-1].end >= self.outn*8:
            n = 1
            while n < len(self._tmp) and self._tmp[n-1].end <= (self.outn+1)*8:
                n += 1    # get groups any part in char, start < next output
            a = (self._tmp[-1].end - self.outn*8) // 8
            if a == 0:
                break
            if n == 1:
                self.color1(a, self._tmp[0].color)
            elif n == 2:
                spt = self._tmp[0].end % 8
                self.color2(spt, self._tmp[0].color, self._tmp[1].color)
            else:
                # raise NotImplementedError('more than two in a char')
                while len(self._tmp) != 2:
                    self._tmp.pop(1)
                continue
            n = 0
            while n < len(self._tmp) and self._tmp[n].end <= (self.outn)*8:
                n += 1
            self._tmp = self._tmp[n:]  # delete groups all in char

    def color2(self, spt, c1, c2):
        assert 0 <= spt <= 8
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
        if len(self._tmp) == 0:
            pass
        elif len(self._tmp) == 1:
            self.out_str += fend
            self.color2(self._tmp[-1].end % 8, self._tmp[0].color, '')
        else:
            raise ValueError('end with _tmp len>1')
        self.out_str += fend
        return self.out_str


def sync_output(points=[0, 1], colors=['r', 'w']):
    sync = syncer()
    if len(points) != len(colors):
        raise ValueError('points{} and colors{} length must same'
                         .format(len(points), len(colors)))
    for i1, color in zip(points, colors):
        sync.add(i1, color)
    return sync.end()


def Spans_out(Spans, Colors, defalut_color='k', end=80*8):
    points = []
    colors = []
    for sp, clr in zip(Spans, Colors):
        if len(points) == 0 or points[-1] != sp[0]:
            points.append(sp[0])
            colors.append(defalut_color)
        points.append(sp[1])
        colors.append(clr)
    if points[-1] != end:
        points.append(end)
        colors.append(defalut_color)
    return sync_output(points, colors)


if __name__ == '__main__':
    print(sync_output([10, 12, 24, 25], ['r', 'w', 'k', 'c']))
    print(Spans_out([(0, 1), (1, 63), (64, 553), (553, 768)], 'rrrr'))
