import numpy as np

low_black = ' ▁▂▃▄▅▆▇█'
resv = '\033[7m'
fend = '\033[0m'


def plot_y(y, ym, yM, insv=False):
    a = 8/(yM-ym)
    b = (8-a*(yM+ym))/2
    out_str = resv if insv else ''
    y = a*y + b
    y = y.astype(np.int)
    for i in y:
        i = 0 if i < 0 else i
        i = 8 if i > 8 else i
        out_str += low_black[i]
    if insv:
        out_str += fend
    out_str += '\n'
    return out_str


def plot_2line(y, y0=None, yw=None):
    yM = y.max()
    ym = y.min()
    if y0 is None and y0 is None:
        y0 = (ym+yM)/2
        yw = yM-y0
    elif y0 is None:
        y0 = (ym+yM)/2
    elif yw is None:
        yw = max(yM-y0, y0-ym)
    out_str = plot_y(y, y0, y0+yw, insv=False)
    out_str += plot_y(y, y0-yw, y0, insv=True)
    print(out_str)


x = np.linspace(0, 2*np.pi, num=20)
y = np.sin(x)
plot_2line(y)
