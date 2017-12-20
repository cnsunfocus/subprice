#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/9/28'

import zlib
import datetime
import struct

import models

def parse_package2(package):
    offset = 0
    total_len = len(package)
    data_list = []
    while offset< total_len - 1:



        data_bytes = package[offset:offset + data_len]
        offset += data_len
        try:
            print 'try to parse zlib data'
            data_list.append(parse_zlib(data_bytes[4:]))
        except Exception as e:
            print e
            print 'total length is %s, current offset %s' % (total_len, offset)

    return data_list


def parse_package(package):
    offset = 0
    total_len = len(package)
    data_list = []
    while offset< total_len - 1:
        #print 'try to get zlib package length, offset is %s' % offset
        data_len = struct.unpack('i', package[offset:offset+4])[0]

        #print 'zlib package length is %s ' % data_len
        if data_len > 16777216 or data_len < 0:
            #print 'Recv a text package'
            #print package
            return None
        offset += 4

        data_bytes = package[offset:offset + data_len]
        offset += data_len
        try:
            #print 'try to parse zlib data'
            data_list.append(parse_zlib(data_bytes[4:]))
        except Exception as e:
            print e
            #print 'total length is %s, current offset %s' % (total_len, offset)

    return data_list


def parse_zlib(bytes):

    data = models.RealTimeData()

    offset = 0
    decompress_data = zlib.decompress(bytes)
    if len(decompress_data) < 156:
        #print "total length is < 156 bytes"
        return data
    data.time = datetime.datetime.fromtimestamp(struct.unpack('l', decompress_data[offset:4])[0])
    offset += 4

    data.label = struct.unpack('12s', decompress_data[offset:offset+12])[0]
    offset += 12

    data.name  = str(struct.unpack('16s', decompress_data[offset:offset+16])[0]).decode('gbk')
    offset += 16

    data.price3 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.latest_vol = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.open_int = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.price2 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.last_close = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.open = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.high = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.low = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.new_price = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.total_vol = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.total_amount = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_price1 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_price2 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_price3 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_price4 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_price5 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_vol1 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_vol2 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_vol3 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_vol4 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.buy_vol5 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_price1 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_price2 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_price3 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_price4 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_price5 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_vol1 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_vol2 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_vol3 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_vol4 = struct.unpack('f', decompress_data[offset:offset+4])[0]
    offset += 4

    data.sell_vol5 = struct.unpack('f', decompress_data[offset:offset+4])[0]

    return data


def tdx_parser(bytes):
    pass

if __name__ == '__main__':
    import  db_util
    import math
    import datetime

    results = []
    f = open('E:\\new_tdx_qh\\vipdoc\ds\\fzline\\76#LSCU.lc5', 'rb')
    # f = open('./test.lc1', 'rb')
    while True:
        bytes = f.read(32)
        if not bytes:
            break

        decode_data = struct.unpack('hhfffffii', bytes)
        u_dt = decode_data[0]
        year = int (math.floor (u_dt / 2048)) + 2004
        month = int (math.floor(u_dt % 2048 / 100))
        day = int (math.floor(u_dt % 2048) % 100)

        hour = int (math.floor(decode_data[1]  / 60))
        min = int (decode_data[1] % 60)
        dt = datetime.datetime(year, month, day, hour, min)
        print decode_data
        results.append((dt, decode_data[2], decode_data[3], decode_data[4], decode_data[5]))

    dbutil = db_util.DbUtil()
    cur = dbutil.get_cursor()
    f = open("./test.lc1", 'wb')
    # cur.execute('select date, open, high, low, close from ctp_cu_1min order by date asc')
    # results = cur.fetchall()
    for r in results:
        dt = r[0]
        u_dt = (dt.year - 2004) * 2048 + dt.month * 100 + dt.day
        u_min = dt.hour * 60 + dt.minute
        packet = struct.pack('hhfffffii', u_dt, u_min, r[1], r[2], r[3], r[4], 0, 0, 0)
        f.write(packet)






