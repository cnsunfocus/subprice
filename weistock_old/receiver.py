#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/9/28'
import socket
import struct
import datetime
import time
from ws_parser import parse_package, parse_zlib
import utils
import models
import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', passwd='', db='future_test')

def read_once():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('121.41.58.181', 22536))
    conn_str = 'm=TJ;u=qq1277;p=abc898;EX_SIZE=1;'
    send_bytes = struct.pack('%ss' % len(conn_str), conn_str)
    print send_bytes

    sock.send(conn_str)

    while True:
        # print 'try to recv package head'
        data = sock.recv(4)
        total_length = struct.unpack('i', data)[0]

        # print 'package length is %s' % total_length
        data = sock.recv(total_length)

        if total_length < 100:
            print 'too short'
            print data
            time.sleep(1)
            continue

        print 'try to parse package'
        parsed_data_list = parse_package(data)
        for d in parsed_data_list:
            print d


def read_multi():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('121.41.58.181', 22536))
    conn_str = 'm=TJ;u=qq1277;p=abc898;EX_SIZE=1;'
    send_bytes = struct.pack('%ss' % len(conn_str), conn_str)
    print send_bytes

    sock.send(conn_str)
    kline = models.KLineData(datetime.datetime.fromtimestamp(0))
    while True:
        # print 'try to recv package head'
        total_length = utils.read_int(sock)
        # print 'package length is %s' % total_length
        if total_length == 16:
            #print utils.read_raw_data(sock, 16)
            break
        read_size = 0

        while read_size < total_length:
            zip_length = utils.read_int(sock)
            read_size += 4

            if zip_length > 16777216:
                # print 'Recv a text package, length is %s' % zip_length
                # data = utils.read_raw_data(sock, zip_length)
                # read_size += zip_length
                # print data
                break

            if zip_length <= 0:
                # print "invalid package length"
                continue

            ori_length = utils.read_int(sock)

            # print 'to recv zip pacakge, length is %s, ori length is %s' %  (zip_length, ori_length)
            data = utils.read_raw_data(sock, zip_length - 4)

            parsed_data = parse_zlib(data)
            if parsed_data.label.startswith('TJCU'):
                if (is_same_min(kline.time, parsed_data.time)):
                    update(kline, parsed_data)
                else:
                    kline = models.KLineData(parsed_data.time, open = parsed_data.new_price, close = parsed_data.new_price)
                    save(kline)
                #print 'parsed data is %s, name is %s' % (parsed_data, parsed_data.name)

            read_size += zip_length

            # print 'read size is %s' % read_size


def is_same_min(time, dest_time):
    #print "time: %s, dest: %s" %(time, dest_time)
    return time.year == dest_time.year and time.month == dest_time.month and time.day == dest_time.day \
           and time.hour == dest_time.hour and time.minute == dest_time.minute

def update(kline, new_data):
    if kline.high <new_data.new_price:
        kline.high = new_data.new_price

    if kline.low > new_data.new_price:
        kline.low = new_data.new_price

    kline.close = new_data.new_price
    cur = conn.cursor()
    sql = "update lme_cu_1min set high=%s, low = %s, close = %s where date = '%s'" % (kline.high, kline.low, kline.close, kline.time.strftime('%Y-%m-%d %H:%M:00'))
    cur.execute(sql)
    cur.close()

def save(kline):
    cur = conn.cursor()
    sql = "insert into lme_cu_1min (date, open, close, high, low, volume) values ('%s', %s, %s, 0, 0, 0)" % (kline.time.strftime('%Y-%m-%d %H:%M:00'), kline.open, kline.close)
    cur.execute(sql)
    cur.close()


if __name__ == '__main__':
    read_multi()
    pass
