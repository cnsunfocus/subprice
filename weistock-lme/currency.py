#! usr/bin/python
# coding=utf-8
__author__ = 'phezzan'
import httplib2
from urllib import urlencode
import datetime
import time
import MySQLdb
import HTMLParser
import config
import math


def is_trading_day(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    if dt.weekday() >= 5:  # TODO 周末不处理， 需要增加法定节假日
        return False

    return True


def get_currency(date=''):
    h2 = httplib2.Http()

    headers = {'Host': 'srh.bankofchina.com',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
               'Cookie': 'JSESSIONID=0000Jl0VAKZrqrH5qJxY_WXG6kV:-1',
               'If-Modified-Since': 'Sun, 21 Feb 2016 08:27:12 GMT',
               'Origin': 'http://srh.bankofchina.com',
               'Referer': 'http://srh.bankofchina.com/search/whpj/search.jsp',
               'Upgrade-Insecure-Requests': '1',
               }

    resp, content = h2.request(uri='http://srh.bankofchina.com/search/whpj/search.jsp', method='GET',
                               headers=headers)
    body = {'pjname': '1316', 'erectDate': date, 'nothing': date}

    content = ''
    headers['Cookie'] = resp['set-cookie']
    resp, content = h2.request(uri='http://srh.bankofchina.com/search/whpj/search.jsp', method='POST',
                               body=urlencode(body), headers=headers)
    # for line in open('d:/1.xml'):
    #    content += line
    data = []
    parser = MyHTMLParser(data)
    parser.feed(content)
    return data


class MyHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, data):
        HTMLParser.HTMLParser.__init__(self)
        self.in_td = False
        self.pass_th = False
        self.counter = 0;
        self.tmp_data = data
        self.price = 0.
        self.date = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.in_td = True
        if tag == 'th':
            self.pass_th = True

    def handle_endtag(self, tag):
        self.in_td = False

    def handle_data(self, data):
        if self.in_td and self.pass_th:
            self.counter += 1
            if self.counter == 6:
                self.price = float(data)

            if self.counter == 8:
                self.tmp_data.append({data: self.price})
                self.counter = 0


def calc_currency_step(cur, currency, last_currency, dt=datetime.datetime.now()):
    # cur.execute('select currency, date from t_currency order by id desc limit 2 ;')
    # currency = 0
    # last_currency = 0

    # results = cur.fetchall()
    # currency = results[0][0]
    # last_currency = results[1][0]

    sub_currency = (currency - last_currency) * 100
    sign = 1
    if sub_currency:
        sign = sub_currency / abs(sub_currency)
    step = config.STEP * sign

    if abs(sub_currency) < config.LOWER:
        step = sub_currency

    if abs(sub_currency) > config.UPPER:
        step = math.ceil(sub_currency / 10.0)

    time_delta = datetime.timedelta(hours=1)
    begin_time = dt.replace(hour=config.BEGIN, minute=0, second=0, microsecond=0)
    adjust_currency = last_currency
    sub_currency = adjust_currency - currency

    sign = ori_sign = 1
    if sub_currency:
        sub_currency / abs(sub_currency)

    while abs(sub_currency) > 0:
        adjust_currency += step / 100.0
        if abs(sub_currency) < abs(step / 100.0) or (ori_sign != sign):
            adjust_currency = currency
        cur.execute("insert into t_calc_currency (date, currency) values ('%s', %s);" % (begin_time, adjust_currency))
        begin_time += time_delta

        sub_currency = adjust_currency - currency
        if sub_currency != 0:
            sign = sub_currency / abs(sub_currency)
    pass


if __name__ == '__main__':
    import db_util

    db = db_util.DbUtil()
    cur = db.get_cursor()
    delta = datetime.timedelta(days=1)
    begin = datetime.datetime.strptime('2017-07-31', '%Y-%m-%d')
    last_currency = None
    for i in range(30):
        data = get_currency(begin.strftime("%Y-%m-%d"))
        data.reverse()
        if len(data) > 0:
            currency = data[0].values()[0]
            cur_date = datetime.datetime.strptime(data[0].keys()[0], '%Y.%m.%d %H:%M:%S')
            cur.execute("insert into t_currency (date, currency) values ('%s', %s);" % (cur_date, currency))
            if last_currency:
                calc_currency_step(cur, currency, last_currency, cur_date)
            last_currency = currency
        begin += delta
    db.conn.commit()
    #         for c in data:
    #             latest_currency = c.values()[0]
    #             date = datetime.datetime.strptime(c.keys()[0], '%Y.%m.%d %H:%M:%S')  # .strftime('%Y-%m-%d %H:%M:%S')
    #             if latest_currency == currency:  # 汇率相同， 不操作
    #                 continue
    # db = MySQLdb.connect(host='localhost', user='root', passwd='', db='future')
    # while True:
    #     time.sleep(5)
    #     try:
    #         currency = 0.
    #         old_date = datetime.datetime.now()
    #
    #         cur = db.cursor()
    #         cur.execute('select currency, date from t_currency order by id desc limit 1 ;')
    #         for row in cur.fetchall():
    #             currency = row[0]
    #             old_date = row[1]
    #         print "last currency is %s, date is %s" % (currency, old_date)
    #         # 查到的汇率与最后一条汇率不同，且对应的时间比最后一条晚
    #         data = get_currency()
    #         data.reverse()
    #
    #         for c in data:
    #             latest_currency = c.values()[0]
    #             date = datetime.datetime.strptime(c.keys()[0], '%Y.%m.%d %H:%M:%S')  # .strftime('%Y-%m-%d %H:%M:%S')
    #             if latest_currency == currency:  # 汇率相同， 不操作
    #                 continue
    #
    #             if date < old_date:
    #                 continue
    #
    #             print "new currency is %s, date is %s" % (latest_currency, date)
    #             sql = "insert into t_currency (date, currency) values ('%s', %s);" % (date, latest_currency)
    #             print "update currency [%s], at date [%s]" % (latest_currency, date)
    #             cur.execute(sql)
    #             calc_currency_step(cur, latest_currency, currency)
    #             currency = latest_currency
    #         db.commit()
    #
    #
    #
    #     except Exception as e:
    #         print e
