#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/9/28'
import models
import MySQLdb
import httplib2
import datetime
import time
import json
import utils
import traceback
import config

conn = MySQLdb.connect(host='localhost', user='root', passwd='password', db='future_test')
username = 'yuantao'
password = 'iloveyou'
#username = 'test'
#password = '8e6a'
# all_url = 'http://db2015.wstock.cn/wsDB_API2/kline.php?r_type=2&qt_type=1&symbol=%s&u=%s&p=%s&return_t=3&q_type=0' \
#           '&desc=1&stime=%s&etime=%s&num=10000'

all_urls = {
    "SCcu": 'http://db2015.wstock.cn/wsDB_API2/kline.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&stime=%s&etime=%s&num=240',
    "LECA": 'http://db2015.wstock.cn/wsDB_API2/kline_t.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&tf=WFUSDCNY&tfd=0&stime=%s&etime=%s&num=240'
}

urls = {
    "SCcu": 'http://db2015.wstock.cn/wsDB_API2/kline.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&num=240',
    "LECA": 'http://db2015.wstock.cn/wsDB_API2/kline_t.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&tf=WFUSDCNY&tfd=0&num=240'
}

#url = 'http://db2015.wstock.cn/wsDB_API2/kline.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&num=100'
#url = 'http://db2015.wstock.cn/wsDB_API2/kline_t.php?r_type=2&qt_type=1&symbol=%s&u=yuantao&p=iloveyou&return_t=3&q_type=0&desc=1&tf=WFUSDCNY&tfd=0'
def query_data(url):
    request = httplib2.Http()
    response, content = request.request(url)
    print url
    if response.status != 200:
        print url
        raise Exception('Request url failed. Error msg is %s', content)

    return json.loads(content)


def save_or_update(k, symbol='TJCU'):
    data = models.KLineData()
    data.time = datetime.datetime.strptime(k['Date'], '%Y-%m-%d %H:%M:00')

    hour = data.time.hour
    min = data.time.minute

    if data.time.second > 0:
        print data.time

    if hour == 1 and min > 0:
        return

    if hour > 1 and hour<9:
        return

    if hour == 11 and min > 30:
        return

    if hour>11 and hour<13:
        return

    if hour == 13 and min < 30:
        return

    if hour == 15 and min > 0:
        return

    if hour > 15 and hour <21:
        return

    if hour == 21 and min == 0:
        return

    data.close = float(k['Close'])
    data.open = float(k['Open'])
    data.low = float(k['Low'])
    data.high = float(k['High'])

    table='lme_cu_1min'

    if symbol==config.FUTURES:
        table = 'ctp_cu_1min'

    last_data = count( k['Date'], table)
    if last_data:
        update(last_data, data, table)
    else:
        kline = models.KLineData(data.time, open = data.open, close = data.close, low = data.low,high = data.high)
        
        save(kline, table)

def check_data(open_time, close_time, symbol='TJCU'):

    s_time = open_time.strftime('%Y-%m-%d %H:00:00').replace(' ', "%%20")
    e_time  = close_time.strftime('%Y-%m-%d %H:00:00').replace(' ', "%%20")
    key = symbol[0:4]
    url = all_urls[key] % (symbol, s_time, e_time)
    # url = all_url % (symbol, username, password, s_time, e_time)

    for i in range(3):
        time.sleep(1)
        try:
            klines = query_data(url)

            if 'errcode' in klines:
                print 'failed url is :%s, return value is %s' % (url, klines)
                return False

            for k in klines:
                save_or_update(k, symbol)

            return True
        except Exception as e:
            traceback.print_exc()
            print 'failed url is :%s' % url
            return False

    return True


def read_multi():
    open_time, close_time = utils.get_open_close_time()

    for symbol in  config.type_list:
        check_data(open_time, close_time, symbol)

    while True:
        time.sleep(12)
        try:
            for symbol in config.type_list:
                time.sleep(1)
                key = symbol[0:4]
                url = urls[key] % (symbol)
                klines = query_data(url % symbol)
                for k in klines:
                    try:
                        save_or_update(k, symbol)
                    except Exception as e:
                        print k, e
                        traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
            print e


def is_same_min(time, dest_time):
    #print "time: %s, dest: %s" %(time, dest_time)
    return time.year == dest_time.year and time.month == dest_time.month and time.day == dest_time.day \
           and time.hour == dest_time.hour and time.minute == dest_time.minute

def count(date, table):
    sql = "select open, high, low, close from %s where date = '%s'" % (table, date)
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    if result:
        data = models.KLineData()
        data.time = datetime.datetime.strptime(date,  '%Y-%m-%d %H:%M:00')
        data.open = result[0]
        data.high = result[1]
        data.low = result[2]
        data.close = result[3]
        return data
    return None


def update(kline, new_data, table='lme_cu_1min'):
    if kline.high <new_data.close:
        kline.high = new_data.close

    if kline.low > new_data.close:
        kline.low = new_data.close

    kline.close = new_data.close
    
    cur = conn.cursor()
    dts = kline.time.strftime('%Y-%m-%d %H:%M:00')
    sql = "update %s set high=%s, low=%s, close=%s,date='%s' where date='%s'" % (table, kline.high, kline.low, kline.close, dts, dts)
    #print sql
    cur.execute(sql)
    cur.close()

def save(kline, table='lme_cu_1min'):
    cur = conn.cursor()
    sql = "insert into %s (date, open, close, high, low, volume) values ('%s', %s, %s, %s, %s, 0)" % (table, kline.time.strftime('%Y-%m-%d %H:%M:00'), kline.open, kline.close, kline.high, kline.low)
    
    cur.execute(sql)
    cur.close()


if __name__ == '__main__':
    read_multi()
    pass
