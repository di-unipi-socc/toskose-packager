import datetime


def compute_uptime(start, current):
    """ given two UNIX time compute the uptime """
    conv = lambda x: datetime.datetime.fromtimestamp(round(x / 1000))
    return ((conv(current) - conv(start)))
