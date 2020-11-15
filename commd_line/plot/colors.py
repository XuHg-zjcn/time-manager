#  3x 4x  01234567
colors = 'krgybmcw'           # rgb cmykw
fg_name = colors.upper()      # KRGYBMCW foreground 3x
bg_name = colors.lower()      # krgybmcw background 4x
names = fg_name + bg_name
fg_nums = list(range(30, 38))  # 30, 31...37
bg_nums = list(range(40, 48))  # 40, 41...47
nums = fg_nums + bg_nums
color_dict = dict(zip(names, nums))

fend = '\033[0m'  # reset to defalut


def style_str(nums):
    """get style code \033[a;b;cm"""
    assert 1 <= len(nums) <= 3
    ret = '\033['
    for i in nums:
        ret += '{};'.format(i)
    ret = ret[:-1] + 'm'
    return ret


def style_code(color='rW'):
    if len(color) == 0:
        return ''
    nums = []
    for c in color:
        if c in color_dict:
            nums.append(color_dict[c])
        elif c.isdecimal():
            nums.append(int(c))
    return style_str(nums)


# tests
if __name__ == '__main__':
    print(style_code('rW'), 12345, fend)  # rW = red bg, White fg
