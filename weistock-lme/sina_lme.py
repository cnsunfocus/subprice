#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2017/8/30'

import requests
import datetime
import time
import models
from multiprocessing import Queue, Process

def get_data(queue):
    import time
    while True:
        try:
            resp =  requests.get("http://hq.sinajs.cn/etag.php?_=%s&list=hf_CAD" % time.time())
            # print resp.content
            #var hq_str_hf_CAD="6797.00,0.0810,6797.00,6798.50,6833.00,6773.00,20:12:15,6791.50,6804.50,1914,0,0,2017-08-30,LME铜";
            result = resp.content[19:-9].split(',')
            dt = datetime.datetime.strptime(result[12]+ " " + result[6], "%Y-%m-%d %H:%M:%S")
            price = result[0]

            kline = models.TimeTick()
            kline.time = time.mktime(dt.timetuple())
            kline.min = dt.minute
            kline.data = float(price)
            queue.put(kline)
            time.sleep(0.1)
        except Exception as e:
            print e


def read_data(queue):
    while True:
        tmp_data = []
        value = queue.get(True)
        if value.min != 0 or value.min != 5:
            time.sleep(1)
            continue
        tmp_data.append(value)
        while True:
            value = queue.get()
            if value.min < tmp_data[-1].min +5:
                tmp_data.append(value)
                continue

            kline = models.KLineData(datetime.datetime.fromtimestamp(tmp_data[0].time).timetuple())
            kline.open = tmp_data[0].data
            kline.high = tmp_data[0].data
            kline.low = tmp_data[0].data
            kline.close = tmp_data[0].data
            for d in tmp_data:
                if d.data > kline.high:
                    kline.high = d.data
                if d.data < kline.low:
                    kline.low = d.data

            tmp_data = []
            tmp_data.append(value)
            print kline
            time.sleep(1)

if __name__=='__main__':
    # 父进程创建Queue，并传给各个子进程：
    q = Queue()

    pw = Process(target=read_data, args=(q,))
    pr = Process(target=get_data, args=(q,))
    # 启动子进程pw，写入:
    pw.start()
    # 启动子进程pr，读取:
    pr.start()
    # 等待pw结束:
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    pr.terminate()











