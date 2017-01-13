#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月14日

@author: lihui1
'''
import db_connect
import pickle
import query_ip
import vip_operation
import record_log
import sys
from db_connect import redis_op as redis_op
import client_operation_tool
import time

def get_vip_status(data_ip,vip):
    return client_operation_tool.fun_main(data_ip,vip)