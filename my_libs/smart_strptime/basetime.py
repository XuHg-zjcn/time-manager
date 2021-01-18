"""
Created on Tue Nov 10 12:37:50 2020

@author: xrj
"""
from enum import Enum        # L0 built-in model
# level of the module is L3


class UType(Enum):
    """Time unit type and time lmr.

    full name and short name
    date short name use Capital letter Y, M, M, WD(WeekDay)
    time short name use small letter   ap(Am/Pm), h, m, s
    time lmr short name use            lt,md,rt (LefT, MiDDle, RighT)
    """

    # date
    year = 0
    month = 1
    day = 2
    Nweek = 3    # N weeks from new year
    weekday = 4  # skip in check_breakpoint
    Y = 0
    M = 1
    D = 2
    NW = 3
    WD = 4
    # time
    ampm = 5     # skip in check_breakpoint
    hour = 6
    minute = 7
    second = 8
    subsec = 9
    milisec = 10
    microsec = 11
    min = 7
    sec = 8
    ap = 5
    h = 6
    m = 7
    s = 8
    ss = 9
    ms = 10
    us = 11
    # time lmr
    left = 12
    midd = 13
    right = 14
    lt = 12
    md = 13
    rt = 14


def dt(U):
    """Generate UType set and dict."""
    Date = {U.Y, U.M, U.D, U.WD}
    Time = {U.ap, U.h, U.m, U.s, U.ss}
    lmr  = {U.lt, U.md, U.rt}
    lmrT = set.union(Time, lmr)
    UxType = {'Date': Date, 'Time': Time, 'lmr': lmr, 'lmrTime': lmrT}
    Char2UType = {'Y': U.Y, 'M': U.M, 'D': U.D, 'W': U.WD,
                  'p': U.ap,'h': U.h, 'm': U.m, 's': U.s, 'S': U.ss}
    return UxType, Char2UType

UxType, Char2UType = dt(UType)
