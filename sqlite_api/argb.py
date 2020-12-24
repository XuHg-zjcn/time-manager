"""
Created on Thu Dec 10 20:22:57 2020

@author: xrj
"""

dict_str2RGB={
'red'     : 0xFF0000,
'yellow'  : 0xFFFF00,
'green'   : 0x00FF00,
'cyan'    : 0x00FFFF,  
'blue'    : 0x0000FF,
'purple'  : 0x7F00FF,
'magenta' : 0xFF00FF,
'black'   : 0x000000,
'gray'    : 0x7F7F7F,
'white'   : 0xFFFFFF}

dict_char2str={
'r': 'red',
'y': 'yellow',
'g': 'green',
'c': 'cyan',
'b': 'blue',
'm': 'magenta',
'k': 'black',
'w': 'white'}


def _out_int(func):
    def warp(paras):
        tup = func(paras)
        ret = 0
        for i in tup:
            ret = (ret << 8) + i
        return ret

    return warp


class ARGB:
    def __new__(cls, R, G, B, A=0xFF):
        self = object.__new__(cls)
        self.R = R
        self.G = G
        self.B = B
        self.A = A
        return self

    def ARGB(self):
        return self.A, self.R, self.G, self.G

    def RGBA(self):
        return self.R, self.G, self.B, self.A

    def RGB(self):
        return self.R, self.G, self.B

    @_out_int
    def ARGBi(self):
        return self.ARGB()

    @_out_int
    def RGBAi(self):
        return self.RGBA()

    @_out_int
    def RGBi(self):
        return self.RGB()

    @classmethod
    def from_rgb(cls, rgb, a=0xFF):
        return cls.__new__(cls, (rgb>>16)&0xff, (rgb>>8)&0xff, rgb&0xff, a)

    @classmethod
    def from_argb(cls, argb):
        if argb is not None:
            argb = int(argb)  # allow use int string argb value, sqlite maybe return string
            return cls.from_rgb(argb%(1<<24), (argb>>24)&0xff)
        else:
            return cls.__new__(cls, 255, 255, 0)  # default

    @classmethod
    def _from_name(cls, x, a=0xFF):
        if len(x) == 1:
            x = dict_char2str[x]
        rgb = dict_str2RGB[x]
        return cls.from_rgb(rgb, a)

    @classmethod
    def from_str(cls, x):
        if x[0] == 't':
            return cls._from_name(x[1:], 0x7F)
        elif x[0] == '#':
            return cls.from_rgb(int(x[1:], 16))
        else:
            return cls._from_name(x)

    def __repr__(self):
        return "ARGB(R={}, G={}, B={}, A={})"\
               .format(self.R, self.G, self.B, self.A)

    def __str__(self):
        return "#{:06x} {:>3.0%}".format(self.RGBi(), self.A/255)
