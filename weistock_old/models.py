#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/9/30'

import time
import datetime
#
# typedef struct tagWS_REALTIME_QUOTEv5
# {
# 	time_t	m_time;					// 成交时间，可google 或 baidu:  java time_t
# 	char	m_szLabel[12];				// 市场前缀+合约代码,以'\0'结尾，市场前缀两字节
# 	char	m_szName[16];				// 合约名称,以'\0'结尾
# 	float	m_fPrice3;					// 沪深股票为成交总笔数；期货是前一交易日结算价；
# 	float	m_fVol2;								// 现量，当前最近一笔成交量
# 	float m_fOpen_Int;							// 仅期货有效，持仓（未平仓合约）
# 	float m_fPrice2;							// 期货当日结算价（盘中为0，收盘后交易所才提供）
#
# 	float	m_fLastClose;								// 昨收价
# 	float	m_fOpen;								// 今开价
# 	float	m_fHigh;									// 最高价
# 	float	m_fLow;									// 最低价
# 	float	m_fNewPrice;								// 最新价
# 	float	m_fVolume;								// 当日总成交量
# 	float	m_fAmount;								// 当日总成交额
#
# 	float	m_fBuyPrice[5];							// 申买价1,2,3,4,5
# 	float	m_fBuyVolume[5];							// 申买量1,2,3,4,5
# 	float	m_fSellPrice[5];							// 申卖价1,2,3,4,5
# 	float	m_fSellVolume[5];							// 申卖量1,2,3,4,5
#
# } WS_REALTIME_QUOTEv5;

class KLineData:
    def __init__(self, t = None, open=0, high=0,low = 0,close=0):
        self.time = t
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def __repr__(self):
        return '%s-%f-%f-%f-%f' % (datetime.datetime.strftime(self.time, '%Y-%m-%d %H:%M:%S'), self.open, self.high, self.low, self.close)



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
        return '%s-%f' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.new_price)

if __name__ == '__main__':
    pass
