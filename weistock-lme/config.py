#!/usr/bin/env python
# -*- coding: utf-8 -*-
__date__ = '2017/6/5'

import json

f = open("./cfg.json")
cfg_json = json.load(f)

FUTURES = cfg_json["futures"]
ACTUAL_GOODS = cfg_json["actual"]
STEP = cfg_json["step"]
UPPER = cfg_json["upper"]
LOWER = cfg_json["lower"]
BEGIN = cfg_json["begin_time"]
type_list = [FUTURES, ACTUAL_GOODS]
