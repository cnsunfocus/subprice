#! usr/bin/python
# coding=utf-8
__author__ = 'phezzan'

import MySQLdb
import models

# lme_sql = "select l.id, l.date, l.open, l.high, l.low, l.close, " \
#           "(select currency from t_currency c where l.date > c.date order by c.id desc limit 1) as currency \
#           from %s l where l.date>='%s' \
#           and l.date <= '%s' order by id;"

ctp_sql = "select id, date, open, high, low, close from %s " \
               "where date >= '%s' " \
               "and date <= '%s' " \
               " order by date asc"

lme_sql = ctp_sql


class DbUtil:
    def __init__(self,host='localhost'):
       
        self.conn = MySQLdb.connect(host=host, user='root', passwd='password', db='future_test')
        
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_cursor(self):
        return self.conn.cursor()

    def get_latest_data(self):
        cur = self.conn.cursor()
        cur.execute("select * from lme_cu_1min where close <>= 0 order by date desc limit 1")
        rss = cur.fetchall()
        return self.parse_data(rss[0])

    def parse_data(self, rs):
        data = models.FutureData()

        if len(rs) == 7:
            data.currency = rs[6]
        data.id = rs[0]
        data.date = rs[1]
        if rs[2] is None or rs[2] == 0:
            data.open = 0
            data.high = 0
            data.low = 0
            data.close = 0
            data.ori_open = 0
            data.ori_high = 0
            data.ori_low = 0
            data.ori_close = 0
        else:
            data.open = rs[2] * (data.currency / 100)
            data.high = rs[3] * (data.currency / 100)
            data.low = rs[4] * (data.currency / 100)
            data.close = rs[5] * (data.currency / 100)

            data.ori_open = rs[2]
            data.ori_high = rs[3]
            data.ori_low = rs[4]
            data.ori_close = rs[5]
        return data

    def get_ctp_data(self, begin_date, end_date):
        sql = ctp_sql % ('ctp_cu_1min', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_lme_data(self,begin_date, end_date):
        sql = lme_sql % ('lme_cu_1min', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_ctp_5min_data(self, begin_date, end_date):
        sql = ctp_sql % ('ctp_cu_5min', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_lme_5min_data(self,begin_date, end_date):
        sql = lme_sql % ('lme_cu_5min', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_price_sub_latestdate(self,begin_date, end_date):
        sql = "select date from sub_price_1min where close != 5000 order by date desc limit 1"
        cur = self.conn.cursor()
        cur.execute(sql)
        for row in cur.fetchall():
            cur.close()
            return row[0]
        cur.close()
        return None

    def parse_sub_data(self,rs):
        data = models.FutureData()
        data.date = rs[1]
        data.open = rs[2]
        data.close = rs[5]
        return data


    def get_price_sub_data(self,begin_date, end_date, table='sub_price_1min'):
        sql = lme_sql % (table, begin_date, end_date)
        cur = self.conn.cursor()
        cur.execute(sql)
        data_list = []
        data_dict = {}
        for row in cur.fetchall():
            data = self.parse_sub_data(row)
            data_list.append(data)
            data_dict[data.date] = data
        return data_list,0,0, data_dict

    def get_ctp_day_data(self, begin_date, end_date):
        sql = ctp_sql % ('ctp_cu_day', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_lme_day_data(self,begin_date, end_date):
        sql = lme_sql % ('lme_cu_day', begin_date, end_date)
        return self.get_data(sql, begin_date, end_date)

    def get_data(self, sql, begin_date, end_date):
        cur = self.conn.cursor()
        cur.execute(sql)
        high = 0.
        low = 99999999.
        data_list = []
        i=0
        for row in cur.fetchall():
            data = self.parse_data(row)
            if data.high > high:
                high = data.high
            if data.low < low and data.close > 0:
                low = data.close
            data_list.append(data)

        return data_list, high, low

    def save_ohlc(self, table, data_list):
        cur = self.conn.cursor()
        for data in data_list:
            try:
                query_sql = "select count(1) from %s where date='%s'" % (table, data.date)
                cur.execute((query_sql))

                row = cur.fetchone()
                if row[0] >= 1:
                    sql_template = "update %s set open=%s, high = %s, low = %s, close = %s, date='%s' where date = '%s'"
                    sql = sql_template %(table, data.open,data.high, data.low,data.close, data.date, data.date)
                    cur.execute(sql)
                else:
                    sql_template = "insert into %s (date, open, high, low, close, volume) values ( '%s', %s, %s, %s, %s, %s)"
                    sql = sql_template % ( table, data.date, data.open, data.high, data.low, data.close, data.volume)
                    cur.execute(sql)

            except Exception as e:
                print e

        cur.close()





