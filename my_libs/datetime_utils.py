import datetime


def date2days1970(x: datetime.date):
    # 719163 == datetime.date(1970, 1, 1).toordinal()
    return x.toordinal() - 719163


def date2ts0(x: datetime.date):
    return datetime.datetime.combine(x, datetime.time()).timestamp()


def time2float(x: datetime.time):
    return 3600*x.hour + 60*x.minute + x.second + x.microsecond/1e6
