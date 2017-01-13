#!/usr/bin/python
#coding:utf8
'''
Created on 2016年11月17日

@author: lihui1
'''
import RedisHelper
import mysql_connect
import record_log

def redis_conn():
    try:
        redis_op=RedisHelper.RedisHelper()
        return redis_op
    except Exception as e:
        record_log.log(e)

def mysql_conn():
    try:
        mysql_op=mysql_connect.Db_conn()
        return mysql_op
    except Exception as e:
        record_log.log(e)

redis_op=redis_conn()
mysql_op=mysql_conn()