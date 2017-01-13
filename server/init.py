#!/usr/bin/python
#coding:utf8
'''
Created on 2016年12月29日

@author: lihui1
'''
from core import server_initialize
from core import vip_init


if __name__=='__main__':
    server_initialize.flush_all_host_configs_into_redis()
    vip_init.vip_init()