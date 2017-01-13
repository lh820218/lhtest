#!/usr/bin/python
#coding:utf8
'''
Created on 2017年1月4日

@author: lihui1
'''
from core import vip_init
from core.db_connect import redis_op
import pickle
from core import ping_check
from core import record_log

def record_trouble_vip(vip):
    record_log.log('%s ping failed' % vip)
    trouble_ip=redis_op.get('trouble_vip')
    if trouble_ip:
        trouble_ip=pickle.loads(trouble_ip)
        trouble_ip.append(vip)
    else:
        trouble_ip=[]
        trouble_ip.append(vip)
    trouble_ip=pickle.dumps(trouble_ip)
    redis_op.set('trouble_vip',trouble_ip)

if __name__=='__main__':
    vip_init.vip_init()
    result=redis_op.get('vip_list')
    result=pickle.loads(result)
    for vip in result:
        result=ping_check.pingServer(vip)
        if not result:
            record_trouble_vip(vip)
            
    