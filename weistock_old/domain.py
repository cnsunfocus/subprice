#! usr/bin/python
# coding=utf-8
__author__ = 'phezzan'
import datetime


class FutureData:
    id = -1
    date = datetime.datetime.strptime('1970-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    open = 0.
    high = 0.
    low = 0.
    close = 0.
    volume = 0
    ori_open = 0.
    ori_high = 0.
    ori_low = 0.
    ori_close = 0.
    currency = 100

    def __repr__(self):
        return '%s, %s,%s,%s,%s' % (self.date, self.open, self.high, self.low, self.close)




