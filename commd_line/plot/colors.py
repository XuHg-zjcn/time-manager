from sqlite_api.colors import ARGB
#  3x 4x  01234567
names = 'krgybmcw'    # rgb cmykw
nums = range(30, 38)  # 30, 31...37
color_dict = dict(zip(names, nums))

fend = '\033[0m'  # reset to defalut


def style_str(nums):
    """get style code \033[a;b;cm"""
    ret = '\033['
    for i in nums:
        ret += '{};'.format(i)
    ret = ret[:-1] + 'm'
    return ret


def strARGB2nums(x, fore_back: bool):
    if isinstance(x, str):
        return [color_dict[x] + fore_back*10]
    elif isinstance(x, ARGB):
        rgb = x.RGB()
        return [38 + fore_back*10, 2] + list(rgb)


def style_code(fore, back):
    nums = []
    if fore is not None:
        nums += strARGB2nums(fore, False)
    if back is not None:
        nums += strARGB2nums(fore, True)
    return style_str(nums)

# tests
if __name__ == '__main__':
    print(style_code('rW'), 12345, fend)  # rW = red bg, White fg
