#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/9/30'

import time
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


class KLineData:
    def __init__(self, t, open=0, high=0,low = 0,close=0):
        self.time = t
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def __repr__(self):
        return '%s-%f-%f-%f-%f' % (time.strftime('%Y-%m-%d %H:%M:%S', self.time), self.open, self.high, self.low, self.close)

class TimeTick:
    def __init__(self):
        self.time = -1
        self.min = -1
        self.data = 0.0

    def __repr__(self):
        return "%s,%s" % (datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'), str(self.data))

class RealTimeData:
    def __init__(self):
        self.time = None  #成交时间
        self.label = '' #市场前缀+合约代码
        self.name = '' #合约名称
        self.price3 = 0.0 #沪深股票为成交总笔数；期货是前一交易日结算价；
        self.latest_vol = 0.0 #现量，当前最近一笔成交量
        self.open_int = 0.0 #仅期货有效，持仓（未平仓合约）
        self.price2 = 0.0 #期货当日结算价（盘中为0，收盘后交易所才提供）
        self.last_close = 0.0 #昨收价
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.new_price = 0.0
        self.total_vol = 0.0
        self.total_amount = 0.0

        self.buy_price1 = 0.0
        self.buy_price2 = 0.0
        self.buy_price3 = 0.0
        self.buy_price4 = 0.0
        self.buy_price5 = 0.0

        self.sell_price1 = 0.0
        self.sell_price2 = 0.0
        self.sell_price3 = 0.0
        self.sell_price4 = 0.0
        self.sell_price5 = 0.0

        self.buy_vol2 = 0.0
        self.buy_vol3 = 0.0
        self.buy_vol4 = 0.0
        self.buy_vol5 = 0.0

        self.sell_vol1 = 0.0
        self.sell_vol2 = 0.0
        self.sell_vol3 = 0.0
        self.sell_vol4 = 0.0
        self.sell_vol5 = 0.0

    def __repr__(self):
        return '%s-%s-%f' % (time.strftime('%Y-%m-%d %H:%M:%S'), unicode(self.label), self.new_price)

if __name__ == '__main__':
    pass