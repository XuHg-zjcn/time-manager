import struct
from datetime import datetime

def hex_out(bytes_in):
    return ' '.join(['{:02x}'.format(b) for b in bytes_in])

f=open('places.sqlite', 'rb')
seq = b'\x00\x05\xb0'
i = 0
n_found = 0
fr =f.read()
    
last_bi = 0
print('{:<6}|{:^9}|{:<5}|{:^47}|{:^19}|{:^47}'.format('found', 'offset', 'diff', 'before', 'date time', 'after'))
for bi, byte in enumerate(fr):
    if byte == seq[i]:
        if i == 2:
            bi0 = bi-2
            diff_bi = bi0 - last_bi
            i = 0
            n_found += 1
            if n_found % 100 == 0:
                ho1 = hex_out(fr[bi0-16:bi0])
                t_bytes = fr[bi0:bi0+8]
                ho2 = hex_out(fr[bi0+8:bi0+24])
                t_long = struct.unpack('>Q', t_bytes)[0]
                dati = datetime.fromtimestamp(t_long//1e6)
                print('{:>6}|{:>9}|{:>5}|{}|{}|{}'.format(n_found, bi0, diff_bi, ho1, dati, ho2))
            last_bi = bi0
        i += 1
    else:
        i = 0
f.close()
print(n_found)
