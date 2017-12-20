#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/10/12'
import httplib2
import json
import datetime
if __name__ == '__main__':
    request = httplib2.Http()
    username = 'yuantao'
    password = 'iloveyou'
    #url = 'http://db2015.wstock.cn/wsDB_API/kline.php?r_type=2&;qt_type=1&symbol=SCcu0001&u=test&p=8e6a&return_t=3&q_type=0&desc=0&stime=2016-01-04%2009:00:00&etime=2016-02-04%2023:59:59&num=200000'
    url = 'http://db2015.wstock.cn/wsDB_API/kline.php?r_type=2&qt_type=1&symbol=TJCU,SCcu0001&u=%s&p=%s&return_t=3&q_type=0&desc=1&stime=2017-03-29%%2009:00:00&etime=2017-03-29%%2023:59:59' % (username, password)

    response, content = request.request(url)

    print response, content
    for c in json.loads(content):
        print c
        #print datetime.datetime.strptime(c['Date'], '%Y-%m-%d %H:%M:%S'), c['Close'], c['Open']
    print len(json.loads(content))
