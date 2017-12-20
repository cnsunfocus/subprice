#!/usr/bin/env python
# -*- coding: GBK -*-
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
            print("��������������ݵ�%sʱ�䣬ʱ���ʽ�� \"2016-08-01 09:00:00\" �����˫����:" % msg)
            print ""
            dt_str = str(input(">"))
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            return dt
        except Exception as e:
            print("ʱ���ʽ��������������,������Ϣ[%s]" % e.message)



if __name__ == '__main__':
    dbutil = db_util.DbUtil()

    # open_time = read_date("����")
    # close_time = read_date("����")

    # recv_data.check_data(open_time, close_time, 'TJCU')
    # time.sleep(1)
    # recv_data.check_data(open_time, close_time, 'SCcu0001')
    # time.sleep(1)
    #
    # calc.calc_sub_price(open_time, close_time)
    # merge.merge(open_time, close_time)
    #
    # begin = datetime.datetime(year=2016, month=9,day=2,hour=9,minute=0,second=0,microsecond=0)
    # end = datetime.datetime(year=2016, month=10,day=13,hour=1,minute=0,second=0,microsecond=0)
    begin = read_date("����")
    end = read_date("����")
    delta = datetime.timedelta(hours=12)

    delta1 = datetime.timedelta(days=4)
    while begin < end:
        time.sleep(1)
        open_time, close_time = utils.get_open_close_time(begin)
        if not utils.is_trading_day(open_time):
            begin += delta
            continue

        res = recv_data.check_data(open_time, close_time, 'TJCU')
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


