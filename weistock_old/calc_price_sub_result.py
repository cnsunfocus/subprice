#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import time
import datetime
import domain
import db_util
import utils

dbutil = db_util.DbUtil()

def parse_data(rs):
    data = domain.FutureData()
    data.date = rs[0]
    data.open = rs[1]

    data.close = rs[2]
    return data


def calc_sub_price(latest_datetime, end_time = None):
    sql = "select date, open,close from %s where date >= '%s' and date not like '%%09:00:00' and close != 5000  order by date asc"
    ctp_sql = sql % ('ctp_cu_1min', latest_datetime)

    sub_price_sql = "insert into sub_price_1min (date, close) values ('%s',%s)"
    query_sql = "select count(1) from sub_price_1min where date = '%s'"
    calc_sub_sql = "select c.close - l.close from lme_cu_1min l, ctp_cu_1min c where l.date <='%s' and c.date = '%s' order by l.date desc limit 1"
    del_sql = "delete from ctp_cu_1min where date='%s'"

    cur = dbutil.conn.cursor()
    cur.execute(ctp_sql)
    rows = cur.fetchall()

    for row in rows:

        data = parse_data(row)
        if end_time and data.date > end_time:
            break

        cur.execute(query_sql % data.date)
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute(calc_sub_sql % (data.date, data.date))
            result = cur.fetchone()
            if result is None:
                cur.execute(del_sql % data.date)
                continue
            sub_price = result[0]
            cur.execute(sub_price_sql % (data.date, sub_price))
        else:
            cur.execute(calc_sub_sql % (data.date, data.date))
            result = cur.fetchone()
            sub_price = result[0]
            cur.execute("update sub_price_1min set close=%s, date='%s' where date = '%s'" % (sub_price, data.date, data.date))

    cur.close()


if __name__ == '__main__':

    latest_datetime = None

    while True:
        try:
            #if latest_datetime is None:
            latest_datetime = dbutil.get_price_sub_latestdate('', '')

            if latest_datetime is None:
                latest_datetime = datetime.datetime.fromtimestamp(0)

            open_time, close_time = utils.get_open_close_time()

            if latest_datetime >= open_time:  # 如果最新的价差时间晚于开盘时间，则从开盘时间计算价差，防止中间有数据丢失。
                latest_datetime = open_time

            calc_sub_price(latest_datetime)
            time.sleep(6)
        except Exception as e:
            dbutil.close()
            dbutil = db_util.DbUtil()
            print e
