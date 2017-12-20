#! usr/bin/python
# coding=utf-8
__author__ = 'phezzan'
import time
import datetime
import models
import db_util
import utils


def ohlc(sub_list, step, length):
    data = models.FutureData()
    h = 0
    l = 100000

    if length == 5:
        data.open = h = l = sub_list[0].close
    else:
        data.open = h = l = sub_list[0].open

    data.close = sub_list[-1].close

    if len(sub_list) == step:
        data.date = sub_list[-1].date
    else:
        dd = sub_list[0].date
        s = dd.strftime('%H:%M:%S')

        delta = datetime.timedelta(minutes=(step - 1) * length)
        if s == '10:15:00':  # 中间休息15分钟
            delta += datetime.timedelta(minutes=15)
        if s == '11:45:00' and length == 30:
            delta += datetime.timedelta(minutes=120)
        tmp_date = sub_list[0].date + delta
        if tmp_date.hour == 15 and tmp_date.minute > 0:
            tmp_date = tmp_date.replace(minute=0)

        if (tmp_date.hour == 1 and tmp_date.minute > 0) or (tmp_date.hour > 1 and tmp_date.hour < 8):
            tmp_date = tmp_date.replace(hour=1)
            tmp_date = tmp_date.replace(minute=0)

        data.date = tmp_date

    for d in sub_list:
        h = d.close if d.close > h else h
        l = d.close if d.close < l else l

    data.high = h
    data.low = l

    return data


def ohlc2(sub_list, timestamp, step):
    data = models.FutureData()
    h = 0
    l = 100000

    if len(sub_list) == 0:
        data.open = 0
        data.close = 0
        data.date = timestamp
        return data

    if sub_list[0].open == 0:
        data.open = h = l = sub_list[0].close
    else:
        data.open = h = l = sub_list[0].open

    data.close = sub_list[-1].close

    data.date = timestamp

    for d in sub_list:
        if step == 1:
            h = d.close if d.close > h else h
            l = d.close if d.close < l else l
        else:
            h = d.high if d.high > h else h
            l = d.low if d.low < l else l

    data.high = h
    data.low = l
    return data


def merge_data(data_list, seq, step, length):
    merged_data = []
    i = 0
    k = 0
    lens = len(data_list)
    for timestamp in seq:
        tmp_list = []
        while k < lens:
            dt = data_list[k]
            if dt.date <= timestamp:
                tmp_list.append(dt)
                k += 1

            if dt.date >= timestamp or k == lens:
                data = ohlc2(tmp_list, timestamp, step)
                merged_data.append(data)
                break

    return merged_data


def gen_time_sequence(open_time, close_time, period):
    seq = []
    delta = datetime.timedelta(minutes=period)
    offset1 = datetime.timedelta(minutes=15)
    offset2 = datetime.timedelta(minutes=120)
    offset3 = datetime.timedelta(minutes=240)

    timestamp = open_time
    while timestamp < close_time:
        timestamp += delta

        if period == 5:
            if timestamp.hour == 10 and timestamp.minute == 20:
                timestamp += offset1

            if timestamp.hour == 11 and timestamp.minute == 35:
                timestamp += offset2

        if period == 15:
            if timestamp.hour == 10 and timestamp.minute == 30:
                timestamp += offset1

            if timestamp.hour == 11 and timestamp.minute == 45:
                timestamp += offset2

        if period == 30:
            if timestamp.hour == 10 and timestamp.minute == 30:
                timestamp += offset1

            if timestamp.hour == 11 and timestamp.minute == 45:
                timestamp += offset2

        if period == 60:
            if timestamp.hour == 11 and timestamp.minute == 0:
                timestamp += offset1

            if timestamp.hour == 12 and timestamp.minute == 15:
                timestamp += offset2

        if period == 120:
            if timestamp.hour == 11 and timestamp.minute == 0:
                timestamp += offset1

            if timestamp.hour == 13 and timestamp.minute == 15:
                timestamp = timestamp.replace(minute=0, hour=15)

        if period == 240:
            if timestamp.hour == 13 and timestamp.minute == 0:
                timestamp += offset2

        if timestamp > close_time:
            timestamp = close_time

        seq.append(timestamp)

    # print seq.__repr__()
    return seq


def validate(data_list, data_dict, open_time, close_time):
    time_step = datetime.timedelta(minutes=1)
    # stamp = open_time + time_step
    if not utils.is_trading_day(open_time):
        return

    if len(data_list) <= 0:
        print 'invalid day: %s' % open_time
        return

    tmp_time = open_time + time_step

    while tmp_time <= close_time:

        str_date = tmp_time.strftime('%H%M')

        if str_date == '1016' or str_date == '1020':
            tmp_time += 15 * time_step  # 休息15分钟
        elif str_date == '1131':
            tmp_time += 120 * time_step  # 午休

        #if tmp_time not in data_dict:
        #    print 'invalid timestamp: %s' % tmp_time

        tmp_time += time_step


def merge(open_time, close_time, symbol='sub_price_'):
    dbutil = db_util.DbUtil()
    sub_price_data_list, high, low, data_dict \
        = dbutil.get_price_sub_data(open_time, close_time, symbol + '1min')
    validate(sub_price_data_list, data_dict, open_time, close_time)

    # merge 15min
    seq = gen_time_sequence(open_time, close_time, 5)
    sub_price_5min_data_list = merge_data(sub_price_data_list, seq, 1, 5)
    dbutil.save_ohlc(symbol + '5min', sub_price_5min_data_list)

    seq = gen_time_sequence(open_time, close_time, 15)
    sub_price_15min_data_list = merge_data(sub_price_5min_data_list, seq, 3, 5)
    dbutil.save_ohlc(symbol + '15min', sub_price_15min_data_list)

    # merge 30min
    seq = gen_time_sequence(open_time, close_time, 30)
    sub_price_30min_data_list = merge_data(sub_price_15min_data_list, seq, 2, 15)
    dbutil.save_ohlc(symbol + '30min', sub_price_30min_data_list)

    seq = gen_time_sequence(open_time, close_time, 60)
    sub_price_60min_data_list = merge_data(sub_price_30min_data_list, seq, 2, 30)
    dbutil.save_ohlc(symbol + '60min', sub_price_60min_data_list)

    seq = gen_time_sequence(open_time, close_time, 120)
    sub_price_120min_data_list = merge_data(sub_price_60min_data_list, seq, 2, 60)
    dbutil.save_ohlc(symbol + '120min', sub_price_120min_data_list)

    seq = gen_time_sequence(open_time, close_time, 240)
    sub_price_240min_data_list = merge_data(sub_price_60min_data_list, seq, 4, 60)
    dbutil.save_ohlc(symbol + '240min', sub_price_240min_data_list)


if __name__ == '__main__':

    while True:
        try:
            open_time, close_time = utils.get_open_close_time()
            for symbol in ['sub_price_', 'ctp_cu_']:
                merge(open_time, close_time, symbol)

        except Exception as e:
            import traceback
            traceback.print_exc()
        time.sleep(6)
