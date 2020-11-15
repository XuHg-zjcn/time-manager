q4_16 = ' ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█'
q2_4 = ' ▀▄█'
def q4(pix4):
    num = 0
    assert len(pix4) == 4
    for i in pix4[::-1]:
        assert i == 0 or i == 1
        num = num*2 + i
    assert 0 <= num < 16
    return q4_16[num]

