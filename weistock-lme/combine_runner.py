#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2017/8/27'
import calc_price_sub_result as calc
import currency as cu
import data_merge_adv as merge
import utils
import db_util
import config
import receive_request as recv
import traceback

import MySQLdb
import datetime
import time

dbutil = db_util.DbUtil()

urls = {
    "SCcu": 'http://db2015.wstock.cn/wsDB_API2/kline.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1',
    "LECA": 'http://db2015.wstock.cn/wsDB_API2/kline_t.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&tf=WFUSDCNY&tfd=0'
}

def calc_currency():
    try:
        currency = 0.
        old_date = datetime.datetime.now()
        cur = dbutil.get_cursor()
        cur.execute('select currency, date from t_currency order by id desc limit 1 ;')
        for row in cur.fetchall():
            currency = row[0]
            old_date = row[1]

        # 查到的汇率与最后一条汇率不同，且对应的时间比最后一条晚
        data = cu.get_currency()
        data.reverse()

        for c in data:
            lastest_currency = c.values()[0]
            if lastest_currency == currency:  # 汇率相同， 不操作
                continue

            date = datetime.datetime.strptime(c.keys()[0], '%Y.%m.%d %H:%M:%S')  # .strftime('%Y-%m-%d %H:%M:%S')
            if date > old_date:
                continue
            sql = "insert into t_currency (date, currency) values ('%s', %s);" % (date, lastest_currency)
            print "update currency [%s], at date [%s]" % (lastest_currency, date)
            cur.execute(sql)
            currency = lastest_currency
            old_date = date
            dbutil.commit()
    except Exception as e:
        print e


def recv_data():
    try:
        for symbol in config.type_list:
            time.sleep(1)
            key = symbol[0:4]
            url = urls[key]
            klines = recv.query_data(url % symbol)
            # print klines
            for k in klines:
                try:
                    recv.save_or_update(k, symbol)
                except Exception as e:
                    # print k, e
                    traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
        print e


def sub_price(open_time, close_time):
    try:
        # if latest_datetime is None:
        latest_datetime = dbutil.get_price_sub_latestdate('', '')

        if latest_datetime is None:
            latest_datetime = datetime.datetime.fromtimestamp(0)

        if latest_datetime >= open_time:  # 如果最新的价差时间晚于开盘时间，则从开盘时间计算价差，防止中间有数据丢失。
            latest_datetime = open_time

        calc.calc_sub_price(latest_datetime)
    except Exception as e:
        print e


def merge_data(open_time, close_time):
    try:
        for symbol in ['sub_price_', 'ctp_cu_']:
            merge.merge(open_time, close_time, symbol)
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    open_time, close_time = utils.get_open_close_time()
    for symbol in config.type_list:
        recv.check_data(open_time, close_time, symbol)

    while True:
        try:
            time.sleep(10)
            # calc_currency()
            recv_data()
            print "receive data"
            sub_price(open_time, close_time)
            print "sub_price data"
            
            merge_data(open_time, close_time)
            print "merge data"

        except Exception as e:
            print e

    pass
