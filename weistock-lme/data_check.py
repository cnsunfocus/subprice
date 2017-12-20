#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2016/7/1'
import db_util
import datetime
import time
import utils
dbutil = db_util.DbUtil()
from data_merge_adv import gen_time_sequence
ctp_sql = "select id, date, open, high, low, close from %s " \
               "where date >= '%s' " \
               "and date <= '%s' " \
               " order by date asc"

lme_sql = ctp_sql

cur = dbutil.get_cursor()

def get_price_sub_data(begin_date, end_date):
    sql = lme_sql % ('sub_price_60min', begin_date, end_date)
    cur.execute(sql)
    data_list = []
    data_dict = {}
    for row in cur.fetchall():
        data = dbutil.parse_sub_data(row)
        data_list.append(data)
        data_dict[data.date] = data
    return data_list,0,0, data_dict

if __name__ == '__main__':
    begin = datetime.datetime(year=2016, month=1,day=4,hour=9,minute=0,second=0,microsecond=0)
    end = datetime.datetime(year=2016, month=11,day=17,hour=1,minute=0,second=0,microsecond=0)
    delta = datetime.timedelta(hours=12)

    while begin < end:
        open_time, close_time = utils.get_open_close_time(begin)

        seq = gen_time_sequence(open_time, close_time, 60)

        sub_price_data_list, high, low, data_dict = get_price_sub_data(open_time, close_time)
        lens = len(sub_price_data_list)
        if lens <= 0 and utils.is_trading_day(open_time):

            print seq
        for i in range(0, lens,1):
            expect = seq[i]

            if expect not in data_dict:
                print "缺少数据: %s " % expect

        begin += delta




