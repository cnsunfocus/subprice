#!/usr/bin/env python
# -*- coding: UTF8 -*-
__date__ = '2016/7/1'

import datetime
import db_util
import receive_request as recv_data
import calc_price_sub_result as calc
import data_merge_adv as merge
import utils
import time
import config
def read_date(msg):
    while True:
        try:
            print ""
            print("请输入待补充数据的%s时间，时间格式如 \"2016-08-01 09:00:00\" 必须加双引号:" % msg)
            print ""
            dt_str = str(input(">"))
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            return dt
        except Exception as e:
            print("时间格式错误，请重新输入,错误信息[%s]" % e.message)



if __name__ == '__main__':
    dbutil = db_util.DbUtil()

    # open_time = read_date("开盘")
    # close_time = read_date("收盘")

    # recv_data.check_data(open_time, close_time, 'TJCU')
    # time.sleep(1)
    # recv_data.check_data(open_time, close_time, 'SCcu0001')
    # time.sleep(1)
    #
    # calc.calc_sub_price(open_time, close_time)
    # merge.merge(open_time, close_time)
    #
    begin = datetime.datetime(year=2017, month=1,day=1,hour=9,minute=0,second=0,microsecond=0)
    end = datetime.datetime(year=2017, month=10,day=10,hour=1,minute=0,second=0,microsecond=0)
    # begin = read_date("开盘")
    # end = read_date("收盘")
    delta = datetime.timedelta(hours=12)

    delta1 = datetime.timedelta(days=4)
    while begin < end:
        time.sleep(1)
        open_time, close_time = utils.get_open_close_time(begin)
        if not utils.is_trading_day(open_time):
            begin += delta
            continue

        res = recv_data.check_data(open_time, close_time, config.ACTUAL_GOODS)
        if not res:
            print "there is no data between %s - %s" %(open_time, close_time)
            begin += delta
            continue

        time.sleep(1)
        res = recv_data.check_data(open_time, close_time, config.FUTURES)

        if not res:
            cur = dbutil.get_cursor()
            cur.execute("delete from lme_cu_1min where date >= '%s' and date <= '%s'" % (open_time, close_time))


        calc.calc_sub_price(begin, close_time)
        for prefix in ['ctp_cu_', 'sub_price_']:
            merge.merge(open_time, close_time, prefix)

        #begin = close_time
        begin += delta


