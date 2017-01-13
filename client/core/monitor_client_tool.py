#!/usr/bin/python
#coding:utf8
'''
Created on 2016年12月29日

@author: lihui1
'''

import db_connect
import pickle
import query_ip
import vip_operation
import record_log
import sys

def get_vip_status():
    try:
        data_ip=query_ip.get_data_ip()
        vip=vip_operation.read_redis_get_vip(data_ip)
        redis_op=db_connect.redis_op
    except:
        record_log.log('get data_ip or vip error,please check!')
        sys.exit(1)
