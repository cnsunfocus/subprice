#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/10/8'

import struct
import datetime

def is_trading_day(dt = None):
    if dt is None:
        dt = datetime.datetime.now()
    if dt.weekday() >= 5:  # TODO 周末不处理， 需要增加法定节假日
        return False

    return True

def get_open_close_time(now = None):

    if not now:
        now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)

    open_time = now
    close_time = now
    if now.hour >= 9 and now.hour <=20:
        open_time = now.replace(hour=9,minute=0,microsecond=0, second =0)
        close_time = now.replace(hour=15,minute=0,microsecond=0, second =0)

    if now.hour >=21 and now.hour<=23:
        open_time = now.replace(hour=21,minute=0,microsecond=0, second =0)
        close_time = now.replace(hour=1,minute=0,microsecond=0, second =0) + delta

    if now.hour>=0 and now.hour<=8:
        open_time = now.replace(hour=21,minute=0,microsecond=0, second =0) - delta
        close_time = now.replace(hour=1,minute=0,microsecond=0, second =0)

    return open_time, close_time

def read_int(sock):
    data = read_raw_data(sock, 4)
    return struct.unpack('i',data)[0]

def read_raw_data(sock, buff_size):
    total_content = ''
    total_recv = 0
    while total_recv < buff_size:
        tmp = sock.recv(buff_size - total_recv)
        total_content += tmp
        total_recv = len(total_content)

    return total_content


if __name__ == '__main__':
    import MySQLdb
    import datetime
    conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='future')
    cur = conn.cursor()
    cur.execute("select date from ctp_cu_1min where date >='2016-02-24 00:00:00' and date <='2016-02-24 23:00:00'")
    rows = cur.fetchall()
    o = datetime.datetime.strptime('2016-10-13', '%Y-%m-%d')
    d = datetime.datetime.strptime('2016-02-24', '%Y-%m-%d')
    delta = o-d
    for row in rows:
        dt = row[0] + delta
        sql = "update ctp_cu_1min set date ='%s' where date = '%s'" % (dt, row[0])
        print sql
        cur.execute(sql)

    pass
